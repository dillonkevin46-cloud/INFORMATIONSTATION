from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'category', 'ip_address', 'is_monitored', 'assigned_user', 'purchase_date', 'warranty_expiry', 'notes']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'type': 'date'}),
        }
