import os
from datetime import timedelta
from importlib import import_module

import qrcode
from django.conf import settings
from django.contrib import auth
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from otpauth import OtpAuth

from problem.models import Problem
from utils.constants import ContestRuleType
from options.options import SysOptions
from utils.api import APIView, validate_serializer, CSRFExemptAPIView
from utils.captcha import Captcha
from utils.shortcuts import rand_str, img2base64, datetime2str
from ..decorators import login_required
from ..models import User, UserProfile, AdminType
from ..serializers import (ApplyResetPasswordSerializer, ResetPasswordSerializer,
                           UserChangePasswordSerializer, UserLoginSerializer,
                           UserRegisterSerializer, UsernameOrEmailCheckSerializer,
                           RankInfoSerializer, UserChangeEmailSerializer, SSOSerializer)
from ..serializers import (TwoFactorAuthCodeSerializer, UserProfileSerializer,
                           EditUserProfileSerializer, ImageUploadForm)
from ..tasks import send_email_async


class UserProfileAPI(APIView):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, **kwargs):
        """
        判断是否登录， 若登录返回用户信息
        """
        user = request.user
        if not user.is_authenticated:
            return self.success()
        show_team_members = False
        username = request.GET.get("username")
        try:
            if username:
                user = User.objects.get(username=username, is_disabled=False)
            else:
                user = request.user
                # api返回的是自己的信息，可以返team_members
                show_team_members = True
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success(UserProfileSerializer(user.userprofile, show_team_members=show_team_members).data)

    @validate_serializer(EditUserProfileSerializer)
    @login_required
    def put(self, request):
        if not SysOptions.allow_register:
            return self.error("Registration has closed, no profile editing allowed")

        data = request.data
        data["team_name"] = data["team_name"].strip()

        user_profile = request.user.userprofile
        if data["team_name"] != getattr(user_profile, "team_name"):
            if UserProfile.objects.filter(team_name=data["team_name"]).exists():
                return self.error("Team name already exists")

        data["team_members"][0]["email"] = getattr(user_profile, "team_members")[0]["email"]
        for k, v in data.items():
            setattr(user_profile, k, v)
        user_profile.save()
        return self.success(UserProfileSerializer(user_profile, show_team_members=True).data)


class TwoFactorAuthAPI(APIView):
    @login_required
    def get(self, request):
        """
        Get QR code
        """
        user = request.user
        if user.two_factor_auth:
            return self.error("2FA is already turned on")
        token = rand_str()
        user.tfa_token = token
        user.save()

        label = f"{SysOptions.website_name_shortcut}:{user.username}"
        image = qrcode.make(OtpAuth(token).to_uri("totp", label, SysOptions.website_name.replace(" ", "")))
        return self.success(img2base64(image))

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def post(self, request):
        """
        Open 2FA
        """
        code = request.data["code"]
        user = request.user
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = True
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid code")

    @login_required
    @validate_serializer(TwoFactorAuthCodeSerializer)
    def put(self, request):
        code = request.data["code"]
        user = request.user
        if not user.two_factor_auth:
            return self.error("2FA is already turned off")
        if OtpAuth(user.tfa_token).valid_totp(code):
            user.two_factor_auth = False
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid code")


class CheckTFARequiredAPI(APIView):
    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        Check TFA is required
        """
        data = request.data
        result = False
        if data.get("username"):
            try:
                user = User.objects.get(username=data["username"])
                result = user.two_factor_auth
            except User.DoesNotExist:
                pass
        return self.success({"result": result})


class UserLoginAPI(APIView):
    @validate_serializer(UserLoginSerializer)
    def post(self, request):
        """
        User login api
        """
        data = request.data
        user = auth.authenticate(username=data["username"], password=data["password"])
        # None is returned if username or password is wrong
        if user:
            if user.is_disabled:
                return self.error("Your account has been disabled")
            if not user.two_factor_auth:
                auth.login(request, user)
                return self.success("Succeeded")

            # `tfa_code` not in post data
            if user.two_factor_auth and "tfa_code" not in data:
                return self.error("tfa_required")

            if OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                auth.login(request, user)
                return self.success("Succeeded")
            else:
                return self.error("Invalid two factor verification code")
        else:
            return self.error("Invalid username or password")


class UserLogoutAPI(APIView):
    def get(self, request):
        auth.logout(request)
        return self.success()


class UsernameOrEmailCheck(APIView):
    @validate_serializer(UsernameOrEmailCheckSerializer)
    def post(self, request):
        """
        check username or email is duplicate
        """
        data = request.data
        # True means already exist.
        result = {
            "username": False,
            "email": False,
            "team_name": False
        }
        if data.get("username"):
            result["username"] = User.objects.filter(username=data["username"].strip().lower()).exists()
        if data.get("email"):
            result["email"] = User.objects.filter(email=data["email"].strip().lower()).exists()
        if data.get("team_name"):
            result["team_name"] = UserProfile.objects.filter(team_name=data["team_name"].strip().lower()).exists()
        return self.success(result)


class UserRegisterAPI(APIView):
    @validate_serializer(UserRegisterSerializer)
    def post(self, request):
        """
        User register api
        """
        if not SysOptions.allow_register:
            return self.error("Registration has closed")

        data = request.data
        data["email"] = data["email"].strip().lower()
        data["username"] = data["username"].strip().lower()
        data["team_name"] = data["team_name"].strip()
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        if User.objects.filter(username=data["username"].lower()).exists():
            return self.error("Username already exists")
        if UserProfile.objects.filter(team_name=data["team_name"]).exists():
            return self.error("Team name already exists")
        if User.objects.filter(email=data["email"]).exists():
            return self.error("Email already exists")
        if len(data["team_members"]) < 1 or len(data["team_members"]) > 4:
            return self.error("Invalid member info")
        user = User.objects.create(username=data["username"], email=data["email"])
        user.set_password(data["password"])
        user.save()
        UserProfile.objects.create(user=user, team_members=data["team_members"], team_name=data["team_name"])
        for team_member in data["team_members"]:
            render_data = {
                "username": user.username,
                "name": team_member["name"],
                "website_name": SysOptions.website_name,
                "website_link": f"{SysOptions.website_base_url}",
                "captain_name": data["team_members"][0]["name"],
                "password": data["password"],
                "team_name": data["team_name"]
            }
            email_html = render_to_string("registration_confirmation_email.html", render_data)
            send_email_async.send(from_name=SysOptions.website_name,
                                  to_email=team_member["email"],
                                  to_name=team_member["name"],
                                  subject="Welcome to TeamsCode Contests",
                                  content=email_html)
            return self.success("Succeeded")


class UserChangeEmailAPI(APIView):
    @validate_serializer(UserChangeEmailSerializer)
    @login_required
    def post(self, request):
        data = request.data
        user = auth.authenticate(username=request.user.username, password=data["password"])
        if user:
            if user.two_factor_auth:
                if "tfa_code" not in data:
                    return self.error("tfa_required")
                if not OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                    return self.error("Invalid two factor verification code")
            data["new_email"] = data["new_email"].lower()
            if User.objects.filter(email=data["new_email"]).exists():
                return self.error("The email is owned by other account")
            user.email = data["new_email"]
            user.save()
            user_profile = request.user.userprofile
            team_members = getattr(user_profile, "team_members")
            team_members[0]["email"] = data["new_email"]
            setattr(user_profile, "team_members", team_members)
            user_profile.save()
            return self.success("Succeeded")
        else:
            return self.error("Wrong password")


class UserChangePasswordAPI(APIView):
    @validate_serializer(UserChangePasswordSerializer)
    @login_required
    def post(self, request):
        """
        User change password api
        """
        data = request.data
        username = request.user.username
        user = auth.authenticate(username=username, password=data["old_password"])
        if user:
            if user.two_factor_auth:
                if "tfa_code" not in data:
                    return self.error("tfa_required")
                if not OtpAuth(user.tfa_token).valid_totp(data["tfa_code"]):
                    return self.error("Invalid two factor verification code")
            user.set_password(data["new_password"])
            user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid old password")


class ApplyResetPasswordAPI(APIView):
    @validate_serializer(ApplyResetPasswordSerializer)
    def post(self, request):
        if request.user.is_authenticated:
            return self.error("You have already logged in")
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            user = User.objects.get(email__iexact=data["email"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        if user.reset_password_token_expire_time and 0 < int(
                (user.reset_password_token_expire_time - now()).total_seconds()) < 20 * 60:
            return self.error("You can only reset password once per 20 minutes")
        user.reset_password_token = rand_str()
        user.reset_password_token_expire_time = now() + timedelta(minutes=20)
        user.save()
        render_data = {
            "username": user.username,
            "website_name": SysOptions.website_name,
            "link": f"{SysOptions.website_base_url}/reset-password/{user.reset_password_token}"
        }
        email_html = render_to_string("reset_password_email.html", render_data)
        send_email_async.send(from_name=SysOptions.website_name,
                              to_email=user.email,
                              to_name=user.username,
                              subject="Reset Your TeamsCode Password",
                              content=email_html)
        return self.success("Succeeded")


class ResetPasswordAPI(APIView):
    @validate_serializer(ResetPasswordSerializer)
    def post(self, request):
        data = request.data
        captcha = Captcha(request)
        if not captcha.check(data["captcha"]):
            return self.error("Invalid captcha")
        try:
            user = User.objects.get(reset_password_token=data["token"])
        except User.DoesNotExist:
            return self.error("Token does not exist")
        if user.reset_password_token_expire_time < now():
            return self.error("Token has expired")
        user.reset_password_token = None
        user.two_factor_auth = False
        user.set_password(data["password"])
        user.save()
        return self.success("Succeeded")


class SessionManagementAPI(APIView):
    @login_required
    def get(self, request):
        engine = import_module(settings.SESSION_ENGINE)
        session_store = engine.SessionStore
        current_session = request.session.session_key
        session_keys = request.user.session_keys
        result = []
        modified = False
        for key in session_keys[:]:
            session = session_store(key)
            # session does not exist or is expiry
            if not session._session:
                session_keys.remove(key)
                modified = True
                continue

            s = {}
            if current_session == key:
                s["current_session"] = True
            s["ip"] = session["ip"]
            s["user_agent"] = session["user_agent"]
            s["last_activity"] = datetime2str(session["last_activity"])
            s["session_key"] = key
            result.append(s)
        if modified:
            request.user.save()
        return self.success(result)

    @login_required
    def delete(self, request):
        session_key = request.GET.get("session_key")
        if not session_key:
            return self.error("Parameter Error")
        request.session.delete(session_key)
        if session_key in request.user.session_keys:
            request.user.session_keys.remove(session_key)
            request.user.save()
            return self.success("Succeeded")
        else:
            return self.error("Invalid session_key")


class ProfileProblemDisplayIDRefreshAPI(APIView):
    @login_required
    def get(self, request):
        profile = request.user.userprofile
        oi_problems = profile.problems_status.get("problems", {})
        ids = list(oi_problems.keys())
        if not ids:
            return self.success()
        display_ids = Problem.objects.filter(id__in=ids, visible=True).values_list("_id", flat=True)
        id_map = dict(zip(ids, display_ids))
        for k, v in oi_problems.items():
            v["_id"] = id_map[k]
        profile.save(update_fields=["problems_status"])
        return self.success()


class OpenAPIAppkeyAPI(APIView):
    @login_required
    def post(self, request):
        user = request.user
        if not user.open_api:
            return self.error("OpenAPI function is not available")
        api_appkey = rand_str()
        user.open_api_appkey = api_appkey
        user.save()
        return self.success({"appkey": api_appkey})


class SSOAPI(CSRFExemptAPIView):
    @login_required
    def get(self, request):
        token = rand_str()
        request.user.auth_token = token
        request.user.save()
        return self.success({"token": token})

    @method_decorator(csrf_exempt)
    @validate_serializer(SSOSerializer)
    def post(self, request):
        try:
            user = User.objects.get(auth_token=request.data["token"])
        except User.DoesNotExist:
            return self.error("User does not exist")
        return self.success({"username": user.username, "avatar": user.userprofile.avatar, "admin_type": user.admin_type})
