import uuid
from django.db import models
from apps.core.models import TimeStampedModel
from apps.ingestion.models import DataSource, ImportRun

class FeedbackItem(TimeStampedModel):
    """
    The canonical, immutable record of normalized civic feedback across all intake channels.
    Strictly free of citizen names, phone numbers, or private credentials.
    """
    STATUS_CHOICES = [
        ('PENDING_ANALYSIS', 'Pending AI Analysis'),
        ('ANALYZED', 'AI Analyzed'),
        ('REVIEWED', 'Human Review Completed'),
        ('DISCARDED', 'Discarded (Non-Civic / Spam)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, related_name='feedback_items')
    import_run = models.ForeignKey(ImportRun, null=True, blank=True, on_delete=models.SET_NULL, related_name='feedback_items')
    external_id = models.CharField(max_length=255, blank=True, help_text="Channel-specific original ID (e.g. WhatsApp message ID)")
    content_hash = models.CharField(max_length=64, db_index=True, help_text="SHA-256 hash of normalized text to block duplicate ingestion")
    raw_text = models.TextField(help_text="Citizen text preserving Gujarati, Hindi, or English verbatim")
    detected_language = models.CharField(max_length=10, default='und', db_index=True, help_text="gu, hi, en, mixed, und")
    published_at = models.DateTimeField(db_index=True, help_text="Original timestamp from source channel")
    raw_metadata = models.JSONField(default=dict, blank=True, help_text="Permitted technical metadata; strictly PII-free")
    is_synthetic = models.BooleanField(default=False, db_index=True, help_text="Flags mock/demo records explicitly")
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='PENDING_ANALYSIS', db_index=True)

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'Civic Feedback Item'
        verbose_name_plural = 'Civic Feedback Items'
        indexes = [
            models.Index(fields=['data_source', 'external_id']),
            models.Index(fields=['content_hash', 'published_at']),
        ]

    def __str__(self):
        return f"Feedback {str(self.id)[:8]} ({self.get_status_display()})"
