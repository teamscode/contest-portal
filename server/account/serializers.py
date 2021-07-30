from django import forms

from utils.api import serializers, UsernameSerializer

from .models import AdminType, ProblemPermission, User, UserProfile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(min_length=6)
    email = serializers.EmailField(max_length=128)
    captcha = serializers.CharField()


class UserChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(min_length=6)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UserChangeEmailSerializer(serializers.Serializer):
    password = serializers.CharField()
    new_email = serializers.EmailField(max_length=64)
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class GenerateUserSerializer(serializers.Serializer):
    prefix = serializers.CharField(max_length=16, allow_blank=True)
    suffix = serializers.CharField(max_length=16, allow_blank=True)
    number_from = serializers.IntegerField()
    number_to = serializers.IntegerField()
    password_length = serializers.IntegerField(max_value=16, default=8)


class ImportUserSeralizer(serializers.Serializer):
    users = serializers.ListField(
        child=serializers.ListField(child=serializers.CharField(max_length=512)))


class UserAdminSerializer(serializers.ModelSerializer):
    team_members = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission", "team_members",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]

    def get_team_members(self, obj):
        return obj.userprofile.team_members


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    team_members = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.show_team_members = kwargs.pop("show_team_members", False)
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_team_members(self, obj):
        return obj.team_members if self.show_team_members else None


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=128)
    team_members = serializers.CharField(max_length=512, allow_blank=True, allow_null=True)
    password = serializers.CharField(min_length=6, allow_blank=True, required=False, default=None)
    email = serializers.EmailField(max_length=128)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class EditUserProfileSerializer(serializers.Serializer):
    team_members = serializers.CharField(max_length=512, allow_null=True, required=False)
    avatar = serializers.CharField(max_length=256, allow_blank=True, required=False)
    language = serializers.CharField(max_length=32, allow_blank=True, required=False)


class ApplyResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    captcha = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(min_length=6)
    captcha = serializers.CharField()


class SSOSerializer(serializers.Serializer):
    token = serializers.CharField()


class TwoFactorAuthCodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class ImageUploadForm(forms.Form):
    image = forms.FileField()


class FileUploadForm(forms.Form):
    file = forms.FileField()


class RankInfoSerializer(serializers.ModelSerializer):
    user = UsernameSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"
