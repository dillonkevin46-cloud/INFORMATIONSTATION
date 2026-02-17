from django.contrib import admin
from .models import Article, Attachment

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_public', 'updated_at')
    list_filter = ('category', 'is_public')
    search_fields = ('title', 'content')
    inlines = [AttachmentInline]

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('article', 'file', 'uploaded_at')
