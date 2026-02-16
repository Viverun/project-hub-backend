from rest_framework import serializers
from .models import Event
from apps.core.models import User


class EventOrganizerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_picture_url']


class EventSerializer(serializers.ModelSerializer):
    organizer = EventOrganizerSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'image_url', 'location', 'start_date', 'end_date',
                  'organizer', 'status', 'attendee_count', 'capacity', 'tags', 'created_at', 'updated_at']
