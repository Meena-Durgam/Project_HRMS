from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Training, TrainingType
from .forms import TrainingForm, TrainingTypeForm
from django.contrib import messages
from notifications.utils import notify_roles  # ✅ Add this for notifications


@login_required
def training_list(request):
    company = request.user.company
    role = request.user.role

    trainings = Training.objects.filter(company=company).order_by('-id')
    form = TrainingForm(company=company)
    edit_form = None
    edit_training = None

    # Add new training
    if request.method == "POST" and role == "company_owner":
        form = TrainingForm(request.POST, company=company)
        if form.is_valid():
            training = form.save(commit=False)
            training.company = company
            training.save()

           

            messages.success(request, "Training added successfully.")
            return redirect('training_list')

    # Edit training
    if 'edit_id' in request.GET and role == "company_owner":
        edit_training = get_object_or_404(Training, id=request.GET.get('edit_id'), company=company)
        edit_form = TrainingForm(instance=edit_training, company=company)

    context = {
        'trainings': trainings,
        'form': form,
        'edit_form': edit_form,
        'edit_training': edit_training,
    }
    return render(request, 'training_list.html', context)


@login_required
def update_training(request, training_id):
    company = request.user.company
    role = request.user.role
    training = get_object_or_404(Training, id=training_id, company=company)

    if request.method == 'POST' and role == "company_owner":
        form = TrainingForm(request.POST, instance=training, company=company)
        if form.is_valid():
            form.save()

            # ✅ Notify about training update
            

            messages.success(request, "Training updated successfully.")
    return redirect('training_list')


@login_required
def delete_training(request, training_id):
    company = request.user.company
    role = request.user.role
    training = get_object_or_404(Training, id=training_id, company=company)

    if role == "company_owner":
        training.delete()
        messages.success(request, "Training deleted successfully.")
    return redirect('training_list')


@login_required
def training_toggle_status(request, id, status):
    company = request.user.company
    training = get_object_or_404(Training, id=id, company=company)

    if request.user.role == "company_owner":
        training.status = status
        training.save()

       
        messages.success(request, "Training status updated.")
    return redirect('training_list')


# -------------------------
# TRAINING TYPE MANAGEMENT
# -------------------------

from django.db import IntegrityError
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import TrainingType
from .forms import TrainingTypeForm
from notifications.utils import notify_roles

@login_required
def training_type_list(request):
    company = request.user.company
    role = request.user.role

    training_types = TrainingType.objects.filter(company=company).order_by('-id')
    form = TrainingTypeForm()
    edit_forms = {}

    if request.method == 'POST' and role == "company_owner":
        if 'add_training_type' in request.POST:
            form = TrainingTypeForm(request.POST)
            if form.is_valid():
                type_name = form.cleaned_data['type_name'].strip()

                # ✅ Check for duplicates (case-insensitive)
                if TrainingType.objects.filter(company=company, type_name__iexact=type_name).exists():
                    messages.error(request, f"Training type '{type_name}' already exists.")
                else:
                    try:
                        training_type = form.save(commit=False)
                        training_type.company = company
                        training_type.type_name = type_name
  # Save cleaned name
                        training_type.save()

                        

                        messages.success(request, 'Training type added successfully.')
                        return redirect('training_type_list')

                    except IntegrityError:
                        messages.error(request, f"Duplicate entry for training type '{type_name}'. Please try again.")

        elif 'edit_training_type' in request.POST:
            edit_id = request.POST.get('edit_id')
            instance = get_object_or_404(TrainingType, id=edit_id, company=company)
            edit_form = TrainingTypeForm(request.POST, instance=instance)
            if edit_form.is_valid():
                updated_name = edit_form.cleaned_data['type_name'].strip()

                # ✅ Check for duplicate (excluding current instance)
                if TrainingType.objects.filter(company=company, type_name__iexact=updated_name).exclude(id=instance.id).exists():

                    messages.error(request, f"Another training type with name '{updated_name}' already exists.")
                else:
                    try:
                        updated_type = edit_form.save(commit=False)
                        updated_type.type_name = updated_name

                        updated_type.save()

                        
                        messages.success(request, 'Training type updated successfully.')
                        return redirect('training_type_list')

                    except IntegrityError:
                        messages.error(request, f"Duplicate entry for training type '{updated_name}'. Update failed.")

    # Populate edit forms for each training type
    for training_type in training_types:
        edit_forms[training_type.id] = TrainingTypeForm(instance=training_type)

    return render(request, 'training_type.html', {
        'training_types': training_types,
        'form': form,
        'edit_forms': edit_forms,
    })

@login_required
def edit_training_type(request, pk):
    training_type = get_object_or_404(TrainingType, pk=pk)
    if request.method == 'POST':
        form = TrainingTypeForm(request.POST, instance=training_type)
        if form.is_valid():
            updated_type = form.save()

            # ✅ Notify about training type edit
            

            return redirect('training_type_list')
    else:
        form = TrainingTypeForm(instance=training_type)
    return render(request, 'training/edit_training_type.html', {
        'form': form,
        'training_type': training_type
    })


@login_required
def delete_training_type(request, pk):
    company = request.user.company
    training_type = get_object_or_404(TrainingType, pk=pk, company=company)

    if request.user.role == "company_owner":
        deleted_name = training_type.type_name

        training_type.delete()

        # ✅ Notify on deletion
        

        messages.success(request, 'Training type deleted successfully.')
    return redirect('training_type_list')


@login_required
def toggle_training_type_status(request, pk, status):
    company = request.user.company
    training_type = get_object_or_404(TrainingType, pk=pk, company=company)

    if request.user.role == "company_owner":
        training_type.status = status
        training_type.save()

        # ✅ Notify on status change
        

        messages.success(request, 'Training type status updated.')
    return redirect('training_type_list')
