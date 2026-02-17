from django.shortcuts import render, get_object_or_404, redirect
from .models import Ticket
from .forms import TicketForm, TicketMessageForm


def ticket_list(request):
    status = request.GET.get('status')
    if status:
        tickets = Ticket.objects.filter(status=status)
    else:
        tickets = Ticket.objects.all()
    tickets = tickets.order_by('-created_at')
    return render(request, 'tickets/ticket_list.html', {'tickets': tickets})


def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if request.method == 'POST':
        form = TicketMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            if request.user.is_authenticated:
                message.author = request.user
            else:
                # Fallback for demo/no-auth
                from django.contrib.auth import get_user_model
                User = get_user_model()
                message.author = User.objects.first()
            message.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketMessageForm()

    return render(request, 'tickets/ticket_detail.html',
                  {'ticket': ticket, 'form': form})


def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            if request.user.is_authenticated:
                ticket.client = request.user
            else:
                # Fallback for demo/no-auth environment: get first user
                from django.contrib.auth import get_user_model
                User = get_user_model()
                ticket.client = User.objects.first()

            ticket.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketForm()

    return render(request, 'tickets/ticket_form.html', {'form': form})
