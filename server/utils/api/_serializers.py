from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers


class UsernameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    team_name = serializers.SerializerMethodField()
    team_members = serializers.SerializerMethodField()
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    has_culv_flag = serializers.SerializerMethodField()
    hidden = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.need_team_members = kwargs.pop("need_team_members", False)
        self.need_review_data = kwargs.pop("need_review_data", False)
        self.culv_ids = kwargs.pop("culv_ids", frozenset())
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_user_profile(obj):
        try:
            return obj.userprofile
        except ObjectDoesNotExist:
            return None

    def get_team_members(self, obj):
        if not self.need_team_members:
            return None
        profile = self.get_user_profile(obj)
        return profile.team_members if profile else []

    def get_team_name(self, obj):
        profile = self.get_user_profile(obj)
        return profile.team_name if profile else None

    def get_upvotes(self, obj):
        if not self.need_review_data:
            return None
        profile = self.get_user_profile(obj)
        return profile.upvotes if profile else None

    def get_downvotes(self, obj):
        if not self.need_review_data:
            return None
        profile = self.get_user_profile(obj)
        return profile.downvotes if profile else None

    def get_has_culv_flag(self, obj):
        if not self.need_review_data or not self.get_user_profile(obj):
            return None
        return obj.id in self.culv_ids

    def get_hidden(self, obj):
        if not self.need_review_data:
            return None
        profile = self.get_user_profile(obj)
        return profile.hidden if profile else None
