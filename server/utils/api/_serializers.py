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

    def get_team_members(self, obj):
        return obj.userprofile.team_members if self.need_team_members else None

    def get_team_name(self, obj):
        return obj.userprofile.team_name

    def get_upvotes(self, obj):
        return obj.userprofile.upvotes if self.need_review_data else None

    def get_downvotes(self, obj):
        return obj.userprofile.downvotes if self.need_review_data else None

    def get_has_culv_flag(self, obj):
        return obj.id in self.culv_ids if self.need_review_data else None

    def get_hidden(self, obj):
        return obj.userprofile.hidden if self.need_review_data else None
