from django import forms
from .models import Ticket, TicketMessage

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'priority', 'category', 'device']

class TicketMessageForm(forms.ModelForm):
    class Meta:
        model = TicketMessage
        fields = ['content', 'is_internal']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Type your reply here...'}),
        }
