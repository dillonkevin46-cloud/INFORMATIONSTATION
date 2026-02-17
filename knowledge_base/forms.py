from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'category', 'content', 'is_public', 'private_notes']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'private_notes': forms.Textarea(attrs={'rows': 3}),
        }
