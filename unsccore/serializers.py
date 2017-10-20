from rest_framework import serializers
from .models import World

class WorkSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    created = serializers.DateTimeField(required=False)
    
    def create(self, validated_data):
        return World.objects.create(**validated_data)
    
