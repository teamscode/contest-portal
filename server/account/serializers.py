from utils.api import serializers

from .models import AdminType, ProblemPermission, ContestDivision, User, UserProfile


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    tfa_code = serializers.CharField(required=False, allow_blank=True)


class UsernameOrEmailCheckSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    team_name = serializers.CharField(required=False)


class TeamMemberSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64)
    email = serializers.EmailField(max_length=64)
    year = serializers.IntegerField(min_value=1900, max_value=2100)
    parent_email = serializers.EmailField(max_length=64)


class UserRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=64)
    team_name = serializers.CharField(max_length=128)
    password = serializers.CharField(min_length=6)
    email = serializers.EmailField(max_length=64)
    team_members = TeamMemberSerializer(many=True)
    division = serializers.ChoiceField(choices=(ContestDivision.ADVANCED, ContestDivision.INTERMEDIATE, ContestDivision.NOVICE))
    captcha = serializers.CharField()
    source = serializers.CharField(required=True, max_length=128)


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
    team_name = serializers.SerializerMethodField()
    division = serializers.SerializerMethodField()
    source = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission", "team_members", "team_name",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled", "division", "source"]

    def get_team_members(self, obj):
        return obj.userprofile.team_members

    def get_team_name(self, obj):
        return obj.userprofile.team_name

    def get_division(self, obj):
        return obj.userprofile.division

    def get_source(self, obj):
        return obj.userprofile.source


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "admin_type", "problem_permission",
                  "create_time", "last_login", "two_factor_auth", "open_api", "is_disabled"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    team_members = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    division = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        self.show_team_members = kwargs.pop("show_team_members", False)
        super(UserProfileSerializer, self).__init__(*args, **kwargs)

    def get_team_members(self, obj):
        return obj.team_members if self.show_team_members else None

    def get_team_name(self, obj):
        return obj.team_name

    def get_division(self, obj):
        return obj.division


class EditUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField(max_length=64)
    team_name = serializers.CharField(max_length=128)
    team_members = TeamMemberSerializer(many=True)
    division = serializers.ChoiceField(choices=(ContestDivision.ADVANCED, ContestDivision.INTERMEDIATE, ContestDivision.NOVICE))
    password = serializers.CharField(min_length=6, allow_blank=True, required=False, default=None)
    email = serializers.EmailField(max_length=64)
    admin_type = serializers.ChoiceField(choices=(AdminType.REGULAR_USER, AdminType.ADMIN, AdminType.SUPER_ADMIN, AdminType.TESTER))
    problem_permission = serializers.ChoiceField(choices=(ProblemPermission.NONE, ProblemPermission.OWN,
                                                          ProblemPermission.ALL))
    open_api = serializers.BooleanField()
    two_factor_auth = serializers.BooleanField()
    is_disabled = serializers.BooleanField()


class EditUserProfileSerializer(serializers.Serializer):
    team_members = TeamMemberSerializer(many=True)
    division = serializers.ChoiceField(choices=(ContestDivision.ADVANCED, ContestDivision.INTERMEDIATE, ContestDivision.NOVICE))
    team_name = serializers.CharField(max_length=128)
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
