# Generated migration file
# documents/migrations/0002_fix_models.py

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0001_initial'),
    ]

    operations = [
        # Add missing indexes for better performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_document_status ON documents (processing_status);",
            reverse_sql="DROP INDEX IF EXISTS idx_document_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_document_type ON documents (document_type);",
            reverse_sql="DROP INDEX IF EXISTS idx_document_type;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_chunk_document_index ON document_chunks (document_id, chunk_index);",
            reverse_sql="DROP INDEX IF EXISTS idx_chunk_document_index;"
        ),
        
        # Create chat history table
        migrations.CreateModel(
            name='ChatHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
                ('answer', models.TextField()),
                ('confidence_score', models.FloatField(default=0.0)),
                ('chunks_used', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_history', to='documents.document')),
            ],
            options={
                'db_table': 'chat_history',
                'ordering': ['-created_at'],
            },
        ),
    ]