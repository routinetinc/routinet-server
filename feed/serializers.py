from rest_framework import serializers

class Image(serializers.Serializer):
    image = serializers.FileField()