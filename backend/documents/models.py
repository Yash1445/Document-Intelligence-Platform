# documents/models.py
import os
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Document(models.Model):
    """Model to store document metadata"""
    
    PROCESSING_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word Document'),
        ('doc', 'Word Document (Legacy)'),
        ('txt', 'Text File'),
        ('md', 'Markdown'),
    ]
    
    title = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)  # Changed from FileField to CharField for compatibility
    document_type = models.CharField(max_length=10, choices=DOCUMENT_TYPE_CHOICES)
    file_size = models.BigIntegerField()  # Size in bytes
    pages_count = models.IntegerField(default=1)  # Fixed field name consistency
    processing_status = models.CharField(
        max_length=20, 
        choices=PROCESSING_STATUS_CHOICES, 
        default='pending'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        db_table = 'documents'
    
    def __str__(self):
        return self.title
    
    def get_file_extension(self):
        """Get file extension from file path"""
        return os.path.splitext(self.file_path)[1].lower()
    
    def get_file_size_display(self):
        """Get human readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def mark_as_processed(self):
        """Mark document as processed"""
        self.processing_status = 'completed'
        self.processed_at = timezone.now()
        self.save()
    
    def mark_as_failed(self):
        """Mark document processing as failed"""
        self.processing_status = 'failed'
        self.processed_at = timezone.now()
        self.save()

class DocumentChunk(models.Model):
    """Model to store processed document chunks"""
    
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='chunks'
    )
    chunk_index = models.IntegerField()
    chunk_text = models.TextField()  # Fixed field name consistency
    page_number = models.IntegerField(default=1)
    start_char = models.IntegerField(default=0)
    end_char = models.IntegerField(default=0)
    token_count = models.IntegerField(default=0)
    embedding_id = models.CharField(max_length=100, null=True, blank=True)  # ChromaDB ID
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        db_table = 'document_chunks'
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
            models.Index(fields=['document', 'page_number']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"
    
    def get_preview(self, length=100):
        """Get preview of chunk text"""
        if len(self.chunk_text) <= length:
            return self.chunk_text
        return self.chunk_text[:length] + "..."

class ChatHistory(models.Model):
    """Model to store chat history"""
    
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE, 
        related_name='chat_history'
    )
    question = models.TextField()
    answer = models.TextField()
    confidence_score = models.FloatField(default=0.0)
    chunks_used = models.JSONField(default=list)  # Store chunk IDs used for answer
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'chat_history'
    
    def __str__(self):
        return f"Q: {self.question[:50]}..." if len(self.question) > 50 else f"Q: {self.question}"