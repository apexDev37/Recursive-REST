from rest_framework import serializers

from greetings.models import Greeting


class GreetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Greeting
        fields = "__all__"

    greeting_id = serializers.UUIDField(read_only=True)
    greeting_text = serializers.CharField(required=True, max_length=50)
    greeting_created_at = serializers.DateTimeField(required=True)

    def create(self, validated_data):
        """
        Create and return Greeting instance, given validated data.
        """
        return Greeting.objects.create(**validated_data)
