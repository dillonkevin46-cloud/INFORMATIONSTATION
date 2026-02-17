from django.shortcuts import render, get_object_or_404
from .models import FormTemplate

def checklist_list(request):
    checklists = FormTemplate.objects.all().order_by('title')
    return render(request, 'checklists/checklist_list.html', {'checklists': checklists})

def checklist_detail(request, checklist_id):
    checklist = get_object_or_404(FormTemplate, id=checklist_id)
    return render(request, 'checklists/checklist_detail.html', {'checklist': checklist})
