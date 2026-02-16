from django.shortcuts import render, get_object_or_404
from .models import FormTemplate

def checklist_list(request):
    templates = FormTemplate.objects.all().order_by('-created_at')
    return render(request, 'checklists/checklist_list.html', {'templates': templates})

def checklist_detail(request, pk):
    template = get_object_or_404(FormTemplate, pk=pk)
    # This would typically be where you render a form to submit
    return render(request, 'checklists/checklist_detail.html', {'template': template})
