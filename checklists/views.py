from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from .models import FormTemplate, FormSubmission
import json

def checklist_list(request):
    checklists = FormTemplate.objects.all().order_by('title')
    return render(request, 'checklists/checklist_list.html', {'checklists': checklists})

def checklist_detail(request, checklist_id):
    checklist = get_object_or_404(FormTemplate, id=checklist_id)
    
    if request.method == 'POST':
        # Extract data dynamically
        submission_data = {}
        # Ensure 'fields' is parsed as a list of dicts if stored as text, 
        # though models.JSONField usually handles this.
        fields = checklist.fields
        if isinstance(fields, str):
             try:
                 fields = json.loads(fields)
             except:
                 fields = []

        for field in fields:
            label = field.get('label')
            field_type = field.get('type')
            
            # Use label as key for POST data extraction
            if field_type == 'checkbox':
                # Checkbox value is 'on' if checked, else None
                submission_data[label] = (request.POST.get(label) == 'on')
            else:
                submission_data[label] = request.POST.get(label)
        
        # Save submission
        submission = FormSubmission(
            template=checklist,
            data=submission_data,
            completed=True, # Assume completed on submit for now
        )
        if request.user.is_authenticated:
            submission.submitted_by = request.user
        else:
            # Fallback
            User = get_user_model()
            submission.submitted_by = User.objects.first()

        submission.save()
        
        return redirect('checklist_list')

    return render(request, 'checklists/checklist_detail.html', {'checklist': checklist})
