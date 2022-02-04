from rest_framework import serializers


class UsernameSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    team_name = serializers.SerializerMethodField()
    team_members = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.need_team_members = kwargs.pop("need_team_members", False)
        super().__init__(*args, **kwargs)

    def get_team_members(self, obj):
        return obj.userprofile.team_members if self.need_team_members else None

    def get_team_name(self, obj):
        return obj.userprofile.team_name
