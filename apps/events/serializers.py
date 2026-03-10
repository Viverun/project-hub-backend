from rest_framework import serializers
from .models import Event
from django.contrib.auth import get_user_model

User = get_user_model()


class EventOrganizerSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()

    def get_profile_picture_url(self, obj):
        return getattr(obj, 'profile_picture_url', None)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_picture_url']


class EventSerializer(serializers.ModelSerializer):
    organizer = EventOrganizerSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image_url', 'location', 'start_date', 'end_date',
                  'organizer', 'status', 'attendee_count', 'capacity', 'tags', 'created_at', 'updated_at']
