from rest_framework import serializers


class UploadBudgetSerializer(serializers.Serializer):
    file = serializers.FileField()


class DatasetMetadataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    source_sheet = serializers.CharField(allow_blank=True)
    source_file = serializers.CharField(allow_blank=True)
    warnings = serializers.ListField(child=serializers.CharField())
    import_stats = serializers.DictField()
    is_active = serializers.BooleanField()
