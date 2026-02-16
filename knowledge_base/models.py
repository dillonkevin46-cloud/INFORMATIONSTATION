from django.db import models
from django.conf import settings

class Article(models.Model):
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100)
    content = models.TextField(help_text="Markdown or HTML content")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='articles', on_delete=models.SET_NULL, null=True)
    
    is_public = models.BooleanField(default=False, help_text="Visible to clients?")
    private_notes = models.TextField(blank=True, help_text="Internal notes for admins")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    article = models.ForeignKey(Article, related_name='attachments', on_delete=models.CASCADE)
    file = models.FileField(upload_to='kb_attachments/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
