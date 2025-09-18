from django.shortcuts import render, redirect, get_object_or_404
from .models import Trainer
from .forms import TrainerForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from notifications.utils import notify_roles  # ✅ Add this

@login_required
def trainer_list(request):
    company = request.user.company
    trainers = Trainer.objects.filter(company=company).order_by('-id')
    form = TrainerForm()
    edit_forms = {}

    if request.method == "POST":
        if 'edit_trainer_id' in request.POST:
            trainer_id = request.POST.get('edit_trainer_id')
            trainer = get_object_or_404(Trainer, id=trainer_id, company=company)
            edit_form = TrainerForm(request.POST, request.FILES, instance=trainer)
            if edit_form.is_valid():
                updated_trainer = edit_form.save(commit=False)
                updated_trainer.company = company
                updated_trainer.save()

                # ✅ Notify about edit
                notify_roles(
                    roles=['company_owner'],
                    message=f"Trainer '{updated_trainer.name}' has been updated.",
                    url='/trainers/',
                    sender=request.user
                )

                messages.success(request, 'Trainer updated successfully.')
                return redirect('trainer_list')
        else:
            form = TrainerForm(request.POST, request.FILES)
            if form.is_valid():
                trainer = form.save(commit=False)
                trainer.company = company
                trainer.save()

                # ✅ Notify about addition
                notify_roles(
                    roles=['company_owner'],
                    message=f"New trainer '{trainer}' has been added.",
                    url='/trainers/',
                    sender=request.user
                )

                messages.success(request, 'Trainer added successfully.')
                return redirect('trainer_list')

    for trainer in trainers:
        edit_forms[trainer.id] = TrainerForm(instance=trainer)

    return render(request, 'trainers.html', {
        'form': form,
        'trainers': trainers,
        'edit_forms': edit_forms
    })


@login_required
def trainer_toggle_status(request, trainer_id, new_status):
    company = request.user.company
    trainer = get_object_or_404(Trainer, id=trainer_id, company=company)

    if new_status in ['Active', 'Inactive', 'On Leave', 'Terminated']:
        trainer.status = new_status
        trainer.save()

        # ✅ Notify about status change
        notify_roles(
            roles=['company_owner'],
            message=f"Trainer '{trainer}' status changed to {new_status}.",
            url='/trainers/',
            sender=request.user
        )

        messages.success(request, f"Trainer status updated to {new_status}.")
    else:
        messages.error(request, "Invalid status selected.")

    return redirect('trainer_list')


@login_required
def edit_trainer(request, trainer_id):
    company = request.user.company
    trainer = get_object_or_404(Trainer, id=trainer_id, company=company)

    if request.method == 'POST':
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            updated_trainer = form.save(commit=False)
            updated_trainer.company = company
            updated_trainer.save()

            # ✅ Notify about edit
            notify_roles(
                roles=['company_owner'],
                message=f"Trainer '{updated_trainer.first_name} {updated_trainer.last_name}' was edited.",
                url='/trainers/',
                sender=request.user
            )

            messages.success(request, "Trainer updated successfully.")
            return redirect('trainer_list')
    else:
        form = TrainerForm(instance=trainer)

    return render(request, 'trainers.html', {
        'form': form,
        'trainers': Trainer.objects.filter(company=company).order_by('-id'),
        'edit_forms': {trainer.id: form}
    })
