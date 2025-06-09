# documents/serializers.py
from rest_framework import serializers
from .models import Document, DocumentChunk

class DocumentSerializer(serializers.ModelSerializer):
    file_size_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = [
            'id', 'title', 'file_path', 'document_type', 'file_size', 
            'file_size_display', 'pages_count', 'processing_status', 
            'uploaded_at', 'processed_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uploaded_at', 'processed_at', 'updated_at']
    
    def get_file_size_display(self, obj):
        """Get human readable file size"""
        size = obj.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class QuestionSerializer(serializers.Serializer):
    document_id = serializers.IntegerField()
    question = serializers.CharField(max_length=1000)
    num_chunks = serializers.IntegerField(default=3, min_value=1, max_value=10)