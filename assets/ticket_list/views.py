from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Ticket, TicketComment
from clients.models import Client
from .forms import TicketForm, TicketCommentForm
from employee.models import Employee

User = get_user_model()

@login_required
def ticket_list(request):
    company = request.user.company

    tickets = Ticket.objects.filter(company=company).order_by('-created_at')
    users = User.objects.filter(company=company)
    clients = Client.objects.filter(company=company)

    new_tickets = tickets.filter(status='New').count()
    open_tickets = tickets.filter(status='Open').count()
    pending_tickets = tickets.filter(status='Pending').count()
    solved_tickets = tickets.filter(status='Solved').count()
    status_choices = Ticket._meta.get_field('status').choices 

    # ✅ Pass `company=company` to the form
    form = TicketForm(request.POST or None, request.FILES or None, company=company)

    if request.method == 'POST':
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.company = company
            ticket.save()
            form.save_m2m()
            messages.success(request, "Ticket created successfully.")
            return redirect('ticket_list')
        else:
            print("Form Errors:", form.errors)
            messages.error(request, "There were errors in the form. Please correct them.")

    return render(request, 'ticket_list.html', {
        'tickets': tickets,
        'form': form,
        'users': users,
        'clients': clients,
        'new_tickets': new_tickets,
        'open_tickets': open_tickets,
        'pending_tickets': pending_tickets,
        'solved_tickets': solved_tickets,
        'status_choices': status_choices,
    })


@login_required
def edit_ticket(request, pk):
    company = request.user.company
    ticket = get_object_or_404(Ticket, pk=pk, company=company)

    # ✅ Pass `company=company` here too
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, instance=ticket, company=company)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.company = company
            ticket.save()
            form.save_m2m()
            messages.success(request, "Ticket updated successfully.")
            return redirect('ticket_list')
        else:
            print("Edit Form Errors:", form.errors)
            messages.error(request, "Form submission failed. Please correct the errors.")
    else:
        form = TicketForm(instance=ticket, company=company)

    return render(request, 'edit_ticket.html', {
        'form': form,
        'ticket': ticket
    })


@login_required
def delete_ticket(request, pk):
    company = request.user.company
    ticket = get_object_or_404(Ticket, pk=pk, company=company)
    ticket.delete()
    messages.success(request, "Ticket deleted.")
    return redirect('ticket_list')


@login_required
def ticket_detail(request, pk):
    company = request.user.company
    ticket = get_object_or_404(Ticket, pk=pk, company=company)
    comments = ticket.comments.filter(company=company).select_related('user').order_by('created_at')

    if request.method == 'POST':
        if 'submit_comment' in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.user = request.user
                comment.company = company
                comment.save()
                messages.success(request, 'Comment added.')
                return redirect('ticket_detail', pk=ticket.pk)
            else:
                print("Comment Form Errors:", comment_form.errors)
                messages.error(request, "Comment form invalid.")

        elif 'submit_ticket' in request.POST:
            ticket_form = TicketForm(request.POST, request.FILES, instance=ticket, company=company)
            if ticket_form.is_valid():
                updated_ticket = ticket_form.save(commit=False)
                updated_ticket.company = company
                updated_ticket.save()
                ticket_form.save_m2m()
                messages.success(request, 'Ticket updated successfully.')
                return redirect('ticket_detail', pk=ticket.pk)
            else:
                print("Ticket Edit Form Errors:", ticket_form.errors)
                messages.error(request, "Ticket form invalid.")
    else:
        ticket_form = TicketForm(instance=ticket, company=company)
        comment_form = TicketCommentForm()

    return render(request, 'ticket_detail.html', {
        'ticket': ticket,
        'ticket_form': ticket_form,
        'comment_form': comment_form,
        'comments': comments,
    })

from django.views.decorators.http import require_POST
from django.http import JsonResponse
@login_required
@require_POST
def update_ticket_status(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, company=request.user.company)
    new_status = request.POST.get('status')

    if new_status in dict(Ticket._meta.get_field('status').choices):
        ticket.status = new_status
        ticket.save()
        return JsonResponse({'success': True, 'status': new_status})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid status'}, status=400)