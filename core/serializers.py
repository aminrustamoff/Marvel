
from rest_framework import serializers

class SubmissionSerializer(serializers.Serializer):
    # dynamic keys → use DictField
    answers = serializers.DictField(
        child=serializers.CharField(allow_null=True, allow_blank=True),
        allow_empty=True
    )