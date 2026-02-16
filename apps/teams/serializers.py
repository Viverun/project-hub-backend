from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Team, JoinRequest

User = get_user_model()


class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_picture_url']


class TeamSerializer(serializers.ModelSerializer):
    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'description', 'owner', 'members', 'member_count', 'capacity', 'created_at', 'updated_at']


class JoinRequestSerializer(serializers.ModelSerializer):
    user = TeamMemberSerializer(read_only=True)

    class Meta:
        model = JoinRequest
        fields = ['id', 'team', 'user', 'status', 'message', 'created_at']
