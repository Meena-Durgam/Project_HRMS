from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password

from .models import Employee, EmployeeProfile, EmergencyContact,Education,Experience,BankDetails,SalaryAndStatutory
from .forms import EmployeeForm,EmergencyContactForm,EmployeeProfileForm,EducationForm,BankDetailsForm,SalaryAndStatutoryForm, ExperienceForm,SSLCForm
from accounts.models import Company, CustomUser

from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from designation.models import Designation

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db.models import Q

from .models import Employee, EmployeeProfile
from .forms import EmployeeForm
from accounts.models import Company, CustomUser
from designation.models import Designation
from projects.models import Project
from django.forms import modelformset_factory
from django.db import models

# views.py (Refactored with proper structure and model alignment)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from .models import (
    Employee, EmployeeProfile, EmergencyContact, Education,
    Experience, BankDetails, SalaryAndStatutory
)
from .forms import (
    EmployeeForm, EmployeeProfileForm, EmergencyContactForm,
    EducationForm, ExperienceForm, BankDetailsForm, SalaryAndStatutoryForm
)
from accounts.models import Company, CustomUser
from designation.models import Designation
from projects.models import Project
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
@login_required
def get_designations_by_department(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    department_id = request.GET.get('department_id')
    designations = Designation.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse({'designations': list(designations)})

def load_designations(request):
    department_id = request.GET.get('department_id')
    designations = Designation.objects.filter(department_id=department_id, status='Active').values('id', 'name')
    return JsonResponse({'designations': list(designations)})

@login_required
def employee_manage_modal(request):
    company = request.user.company

    # --- Filters ---
    emp_id_query = request.GET.get('employee_id', '').strip()
    emp_name_query = request.GET.get('employee_name', '').strip()
    emp_designation_query = request.GET.get('designation', '').strip()

    # --- View Mode (grid/table) ---
    view_mode = request.GET.get('view_mode') or 'grid'

    # --- Employees Queryset ---
    employees_queryset = Employee.objects.filter(company=company)

    if emp_id_query:
        employees_queryset = employees_queryset.filter(employee_id__icontains=emp_id_query)
    if emp_name_query:
        employees_queryset = employees_queryset.filter(
            Q(first_name__icontains=emp_name_query) |
            Q(last_name__icontains=emp_name_query)
        )
    if emp_designation_query:
        employees_queryset = employees_queryset.filter(designation_id=emp_designation_query)

    # --- Pagination Settings ---
    table_page_size = request.GET.get('table_page_size', 5)
    grid_page_size = request.GET.get('grid_page_size', 6)

    try:
        table_page_size = int(table_page_size)
    except ValueError:
        table_page_size = 5
    try:
        grid_page_size = int(grid_page_size)
    except ValueError:
        grid_page_size = 6

    # --- Table View Pagination ---
    table_paginator = Paginator(employees_queryset, table_page_size)
    table_page_number = request.GET.get('table_page')
    table_employees = table_paginator.get_page(table_page_number)

    # --- Grid View Pagination ---
    grid_paginator = Paginator(employees_queryset, grid_page_size)
    grid_page_number = request.GET.get('grid_page')
    grid_employees = grid_paginator.get_page(grid_page_number)

    # --- Forms ---
    add_form = EmployeeForm(company=company)
    edit_forms = {emp.id: EmployeeForm(instance=emp, company=company) for emp in employees_queryset}

    # --- Handle Form Submission (Add/Edit) ---
    if request.method == 'POST':
        emp_id = request.POST.get('id', '').strip()
        if emp_id:
            emp_instance = get_object_or_404(Employee, id=emp_id, company=company)
            form = EmployeeForm(request.POST, instance=emp_instance, company=company)
        else:
            form = EmployeeForm(request.POST, company=company)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Employee updated successfully.' if emp_id else 'Employee created successfully.')
                return redirect(request.path_info + f"?view_mode={view_mode}")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
            if emp_id:
                edit_forms[int(emp_id)] = form
            else:
                add_form = form

    # --- Designations for filter dropdown ---
    all_designations = Designation.objects.filter(company=company, status='Active')

    return render(request, 'employee/manage_employees.html', {
        'form': add_form,
        'edit_forms': edit_forms,
        'employees_table': table_employees,      # Table view
        'employees_grid': grid_employees,        # Grid view
        'table_page_obj': table_employees,       # Table pagination
        'grid_page_obj': grid_employees,         # Grid pagination
        'employees': employees_queryset,  
        'designations': all_designations,
        'table_page_size': table_page_size,
        'grid_page_size': grid_page_size,
        'filters': {
            'employee_id': emp_id_query,
            'employee_name': emp_name_query,
            'designation': emp_designation_query,
        },
        'view_mode': view_mode,
    })



def ajax_load_designations(request):
    department_id = request.GET.get('department_id')
    designations = Designation.objects.filter(department_id=department_id, status='Active').order_by('name')
    data = [{'id': desig.id, 'name': desig.name} for desig in designations]
    return JsonResponse({'designations': data})


from accounts.models import CustomUser
from django.http import JsonResponse

@login_required
def check_email(request):
    email = request.GET.get('email', '').strip()
    exists = CustomUser.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

def get_employee_data(request, pk):
    emp = Employee.objects.select_related('designation', 'department').get(pk=pk)
    return JsonResponse({
        'id': emp.id,
        'first_name': emp.first_name,
        'last_name': emp.last_name,
        'email': emp.email,
        'designation': emp.designation_id,
        'department': emp.department_id,
        'joining_date': emp.joining_date.strftime('%Y-%m-%d') if emp.joining_date else '',
        'status': emp.status,
        # Don't return password!
    })
def employee_delete(request, pk):
    if request.method == 'POST':
        employee = get_object_or_404(Employee, pk=pk, company=request.user.company)

        # Delete associated user
        if employee.user:
            employee.user.delete()

        # Delete employee record
        employee.delete()

        messages.success(request, 'Employee deleted successfully.')

    return redirect('employee_manage_modal')

@login_required
def admin_update_financial_info(request, employee_id):
    if not request.user.company:  # Replace with your real permission logic
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    employee = get_object_or_404(Employee, id=employee_id)
    statutory, _ = SalaryAndStatutory.objects.get_or_create(employee=employee)
    profile, _ = EmployeeProfile.objects.get_or_create(employee=employee)

    if request.method == 'POST':
        form = SalaryAndStatutoryForm(request.POST, instance=statutory)
        if form.is_valid():
            instance = form.save(commit=False)

            # ✅ Auto calculate totals
            try:
                pf1 = int(request.POST.get('employee_pf_rate', '0').replace('%', ''))
                pf2 = int(request.POST.get('additional_pf_rate', '0').replace('%', ''))
                instance.total_pf_rate = f"{pf1 + pf2}%"
            except:
                instance.total_pf_rate = ''

            try:
                esi1 = int(request.POST.get('employee_esi_rate', '0').replace('%', ''))
                esi2 = int(request.POST.get('additional_esi_rate', '0').replace('%', ''))
                instance.total_esi_rate = f"{esi1 + esi2}%"
            except:
                instance.total_esi_rate = ''

            instance.save()

            # Approval logic
            profile.is_approved = True
            profile.approved_at = timezone.now()
            profile.save()

            messages.success(request, "Financial information updated.")
            return redirect('employee_manage_modal')  # Change to your view
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = SalaryAndStatutoryForm(instance=statutory)

    return render(request, 'employee/employee_detail_view.html', {
        'emp': employee,
        'salary_form': form,
        'profile': profile,
    })

# 🔹 Company Owner/Admin Approves Profile
@login_required
def toggle_employee_profile_approval(request, emp_id):
    emp = get_object_or_404(Employee, id=emp_id)

    if not hasattr(emp, 'profile'):
        messages.warning(request, "Profile not submitted yet.")
        return redirect('manage_employees')

    profile = emp.profile

    if profile.is_approved:
        # 🔻 Unapprove
        profile.is_approved = False
        profile.approved_at = None
        emp.status = 'Pending'
        messages.info(request, "Employee profile has been unapproved.")
    else:
        # ✅ Approve
        profile.is_approved = True
        profile.approved_at = timezone.now()
        emp.status = 'Active'
        messages.success(request, "Employee profile approved successfully.")

    profile.save()
    emp.save()

    return redirect('employee_manage_modal')
from django.forms import modelformset_factory
from django.db import models
from django.forms import modelformset_factory, BaseModelFormSet

# Custom Formset to exclude SSLC from degree_type choices

class CustomEducationFormSet(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.exclude_degree_type = kwargs.pop('exclude_degree_type', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs['exclude_degree_type'] = self.exclude_degree_type
        return super()._construct_form(i, **kwargs)

from django.forms import inlineformset_factory
from .forms import FamilyMemberForm, FamilyMemberFormSet
from .models import FamilyMember
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib import messages
from .models import Employee, EmployeeProfile, BankDetails, EmergencyContact, Experience, Education, FamilyMember
from .forms import (
    EmployeeProfileForm, BankDetailsForm, EmergencyContactForm, ExperienceForm,
    EducationForm, FamilyMemberFormSet
)
from .models import EducationDocument,GovernmentDocument
from .forms import EducationDocumentForm, GovernmentDocumentForm
from django.contrib.auth.decorators import login_required
from django.forms import modelformset_factory, inlineformset_factory
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def employee_profile(request):
    if request.user.role != 'employee':
        messages.error(request, "Unauthorized access.")
        return redirect('home')

    employee = request.user.employee_account
    profile, _ = EmployeeProfile.objects.get_or_create(employee=employee)
    bank, _ = BankDetails.objects.get_or_create(employee=employee)

    # Formset definitions
    EmergencyContactFormSet = modelformset_factory(
        EmergencyContact, form=EmergencyContactForm,
        extra=1, max_num=2, validate_max=True, can_delete=True
    )

    ExperienceFormSet = inlineformset_factory(
        Employee, Experience, form=ExperienceForm, extra=0, can_delete=True
    )

    EducationFormSet = modelformset_factory(
        Education, form=EducationForm, can_delete=True
    )

    FamilyMemberFormSet = modelformset_factory(
        FamilyMember, form=FamilyMemberForm, extra=1, can_delete=True
    )

    if request.method == 'POST':
        submit_type = request.POST.get('submit_type')

        profile_form = EmployeeProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        bank_form = BankDetailsForm(request.POST, instance=bank)
        emergency_formset = EmergencyContactFormSet(
            request.POST,
            queryset=EmergencyContact.objects.filter(employee=employee),
            prefix='emergency'
        )
        experience_formset = ExperienceFormSet(request.POST, instance=employee, prefix='experience')
        sslc_instance = Education.objects.filter(employee=employee, degree_type='SSLC').first()
        sslc_form = SSLCForm(request.POST, instance=sslc_instance, prefix='sslc')
        # ✅ queryset, not instance
        education_formset = EducationFormSet(
            request.POST,
            queryset=Education.objects.filter(employee=employee).exclude(degree_type='SSLC'),
            prefix='edu'
        )
        family_formset = FamilyMemberFormSet(
            request.POST,
            queryset=FamilyMember.objects.filter(employee=employee),
            prefix='family'
        )

        # -------------------
        # PERSONAL INFO
        # -------------------
        if submit_type == 'personal_info' and profile_form.is_valid():
            profile_form.save()
            profile.check_profile_completion()
            messages.success(request, "Personal info updated successfully.")
            return redirect('employee_profile')

        # -------------------
        # EMERGENCY CONTACTS
        # -------------------
        elif submit_type == 'emergency' and emergency_formset.is_valid():
            instances = emergency_formset.save(commit=False)
            for contact in instances:
                contact.employee = employee
                contact.save()
            for obj in emergency_formset.deleted_objects:
                obj.delete()
            profile.check_profile_completion()
            messages.success(request, "Emergency contact details updated successfully.")
            return redirect('employee_profile')

        # -------------------
        # BANK DETAILS
        # -------------------
        elif submit_type == 'bank' and bank_form.is_valid():
            bank_instance = bank_form.save(commit=False)
            bank_instance.employee = employee
            bank_instance.save()
            profile.check_profile_completion()
            messages.success(request, "Bank details updated successfully.")
            return redirect('employee_profile')

        # -------------------
        # EXPERIENCE
        # -------------------
        elif submit_type == 'experience' and experience_formset.is_valid():
            experiences = experience_formset.save(commit=False)
            for exp in experiences:
                exp.employee = employee
                exp.save()
            for obj in experience_formset.deleted_objects:
                obj.delete()
            messages.success(request, "Experience details updated successfully.")
            return redirect('employee_profile')

        # -------------------
        # EDUCATION
        # -------------------
        elif submit_type == 'education' and sslc_form.is_valid() and education_formset.is_valid():
            # Save SSLC
            sslc = sslc_form.save(commit=False)
            sslc.employee = employee
            sslc.degree_type = 'SSLC'
            sslc.save()

            saved_degrees = set(
                Education.objects.filter(employee=employee)
                .exclude(degree_type='SSLC')
                .values_list('degree_type', flat=True)
            )

            for form in education_formset.forms:
                # Skip empty forms (no meaningful data entered)
                if not form.cleaned_data or all(not v for k, v in form.cleaned_data.items() if k != 'DELETE'):
                    continue

                if form.cleaned_data.get('DELETE'):
                    if form.instance.pk:
                        form.instance.delete()
                    continue

                edu = form.save(commit=False)
                edu.employee = employee

                # Only check for duplicates if it's a new entry
                if not edu.pk:
                    if edu.degree_type in saved_degrees:
                        messages.warning(request, f"{edu.get_degree_type_display()} already exists. Skipping duplicate.")
                        continue
                    saved_degrees.add(edu.degree_type)

                edu.save()

            profile.check_profile_completion()
            messages.success(request, "Education details updated successfully.")
            return redirect('employee_profile')


        # -------------------
        # FAMILY MEMBERS
        # -------------------
        elif submit_type == 'family' and family_formset.is_valid():
            instances = family_formset.save(commit=False)
            for member in instances:
                member.employee = employee
                member.save()
            for obj in family_formset.deleted_objects:
                obj.delete()
            profile.check_profile_completion()
            messages.success(request, "Family details updated successfully.")
            return redirect('employee_profile')

        # -------------------
        # GOVERNMENT DOCUMENTS
        # -------------------
        elif submit_type == 'government':
            action = request.POST.get('action')
            doc_id = request.POST.get('document_id')

            # Delete Document
            if action == 'delete' and doc_id:
                doc = get_object_or_404(GovernmentDocument, id=doc_id, employee=employee)
                doc.delete()
                messages.success(request, "Government document deleted successfully.")
                return redirect('employee_profile')

            # Edit Document
            if action == 'edit' and doc_id:
                existing_doc = get_object_or_404(GovernmentDocument, id=doc_id, employee=employee)
                gov_form = GovernmentDocumentForm(request.POST, request.FILES, instance=existing_doc)

                if gov_form.is_valid():
                    doc_type = gov_form.cleaned_data.get('document_type')
                    other_doc_type = gov_form.cleaned_data.get('other_document_type')

                    duplicate_check = GovernmentDocument.objects.filter(
                        employee=employee,
                        document_type=doc_type,
                        other_document_type__iexact=other_doc_type if doc_type == 'Other' else None
                    ).exclude(id=doc_id)

                    if duplicate_check.exists():
                        messages.error(request, f"{doc_type} document already exists.")
                        return redirect('employee_profile')

                    gov_form.save()
                    messages.success(request, "Government document updated successfully.")
                    return redirect('employee_profile')

                # 🔥 Show form field errors
                for field, errors in gov_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                return redirect('employee_profile')

            # Add New Document
            gov_form = GovernmentDocumentForm(request.POST, request.FILES)
            if gov_form.is_valid():
                doc_type = gov_form.cleaned_data.get('document_type')
                other_doc_type = gov_form.cleaned_data.get('other_document_type')

                existing = GovernmentDocument.objects.filter(
                    employee=employee,
                    document_type=doc_type,
                    other_document_type__iexact=other_doc_type if doc_type == 'Other' else None
                )

                if existing.exists():
                    messages.error(request, f"{doc_type} document already uploaded.")
                    return redirect('employee_profile')

                doc = gov_form.save(commit=False)
                doc.employee = employee
                doc.save()

                messages.success(request, "Government document uploaded successfully.")
                return redirect('employee_profile')

            # 🔥 Show form field errors
            for field, errors in gov_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('employee_profile')

        # -------------------
        # EDUCATION DOCUMENTS
        # -------------------
        elif submit_type == 'educationdocument':
            doc_id = request.POST.get('document_id')
            instance = None

            if doc_id:
                instance = get_object_or_404(EducationDocument, id=doc_id, employee=employee)

            edu_form = EducationDocumentForm(
                request.POST,
                request.FILES,
                instance=instance
            )

            if edu_form.is_valid():
                doc = edu_form.save(commit=False)
                doc.employee = employee

                if doc.document_type == 'Other':
                    custom_type = edu_form.cleaned_data.get('other_document_type')
                    if custom_type:
                        doc.document_type = custom_type

                if not doc_id and EducationDocument.objects.filter(
                        employee=employee,
                        document_type=doc.document_type
                ).exists():
                    messages.error(request, f"{doc.document_type} already uploaded.")
                    return redirect('employee_profile')

                doc.save()
                if doc_id:
                    messages.success(request, "Education document updated successfully.")
                else:
                    messages.success(request, "Education document uploaded successfully.")
                return redirect('employee_profile')

            messages.error(request, "Please correct the errors in the form.")
            return redirect('employee_profile')

        elif submit_type == 'delete_educationdocument':
            doc_id = request.POST.get('document_id')
            document = get_object_or_404(EducationDocument, id=doc_id, employee=employee)
            document.delete()
            messages.success(request, "Education document deleted successfully.")
            return redirect('employee_profile')

    else:
        profile_form = EmployeeProfileForm(instance=profile, user=request.user)
        bank_form = BankDetailsForm(instance=bank)
        emergency_formset = EmergencyContactFormSet(
            queryset=EmergencyContact.objects.filter(employee=employee),
            prefix='emergency'
        )
        experience_formset = ExperienceFormSet(instance=employee, prefix='experience')
        sslc_form = SSLCForm(
            instance=Education.objects.filter(employee=employee, degree_type='SSLC').first(),
            prefix='sslc'
        )
        # ✅ queryset, not instance
        education_formset = EducationFormSet(
            queryset=Education.objects.filter(employee=employee).exclude(degree_type='SSLC'),
            prefix='edu'
        )
        family_formset = FamilyMemberFormSet(
            queryset=FamilyMember.objects.filter(employee=employee),
            prefix='family'
        )

    education_documents = EducationDocument.objects.filter(employee=employee)
    government_documents = GovernmentDocument.objects.filter(employee=employee)
    uploaded_documents = government_documents.values_list('document_type', flat=True)
    employee_projects = Project.objects.filter(
        models.Q(team_leader=employee) | models.Q(team_members=employee)
    ).distinct()

    project_stats = []
    for project in employee_projects:
        tasks = project.tasks.all()
        total_tasks = tasks.count()
        completed_tasks = tasks.filter(status="Completed").count()
        in_progress_tasks = tasks.filter(status="In Progress").count()
        to_do_tasks = tasks.filter(status="To Do").count()

        percent_complete = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

        project_stats.append({
            "project": project,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "to_do_tasks": to_do_tasks,
            "percent_complete": percent_complete,
        })
    for project in employee_projects:
        project.total_tasks = project.tasks.count()
        project.completed_tasks = project.tasks.filter(status='Completed').count()

    context = {
        'employee_projects': employee_projects,
        'project_stats': project_stats, 
        'profile': profile,
        'form': profile_form,
        'bank_form': bank_form,
        'emergency_formset': emergency_formset,
        'experience_formset': experience_formset,
        'sslc_form': sslc_form,
        'empty_education_form': education_formset.empty_form,
        'education_formset': education_formset,
        'bank': bank,
        'show_complete_btn': not profile.is_completed,
        'show_edit_btn': profile.is_completed,
        'project_stats': project_stats,
        'employee_id': employee.id,
        'employee': employee,
        'experiences': employee.experiences.all().order_by('-start_date', '-end_date'),
        'family_formset': family_formset,
        'uploaded_documents': uploaded_documents,
        'gov_form': GovernmentDocumentForm(),
        'education_documents': education_documents,
        'government_documents': government_documents,
        'edu_form': EducationDocumentForm(),
    }

    return render(request, 'employee/profile_detail.html', context)



def add_education(request, employee_id):
    employee = get_object_or_404(EmployeeProfile, user=request.user)

    EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=1, can_delete=True)

    if request.method == 'POST':
        sslc_form = EducationForm(request.POST, prefix='sslc')
        formset = EducationFormSet(request.POST, queryset=Education.objects.filter(employee=employee))

        if sslc_form.is_valid() and formset.is_valid():
            sslc = sslc_form.save(commit=False)
            sslc.employee = employee
            sslc.save()

            educations = formset.save(commit=False)
            for edu in educations:
                edu.employee = employee
                edu.save()

            # Handle deletions if applicable
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect('employee_profile')  # Update with correct redirect
    else:
        sslc_form = EducationForm(prefix='sslc', initial={'degree_type': 'SSLC'})
        formset = EducationFormSet(queryset=Education.objects.filter(employee=employee).exclude(degree_type='SSLC'))

    return render(request, 'employee/profile_detail.html', {
        'employee': employee,
        'sslc_form': sslc_form,
        'formset': formset,
    })

@login_required
def company_employee_list(request):
    if request.user.role != "company_owner":
        messages.error(request, "Access denied.")
        return redirect('home')  # Or your preferred fallback route

    if not request.user.company:
        messages.error(request, "No company associated with your account.")
        return redirect('home')

    # Filter employees by company of the logged-in company owner
    employees = Employee.objects.filter(company=request.user.company)

    return render(request, 'employee/company_employee_list.html', {'employees': employees})

from django.http import JsonResponse
def get_designations(request):
    department_id = request.GET.get('department_id')
    designations = Designation.objects.filter(department_id=department_id).values('id', 'name')
    return JsonResponse(list(designations), safe=False)

@login_required
def view_profile(request, pk):
    emp = get_object_or_404(Employee, pk=pk)

    profile = getattr(emp, 'profile', None)
    emergency_contacts = emp.emergency_contacts.all()
    educations = emp.education.all()
    experiences = emp.experiences.all()

    # ✅ Bank Details (OneToOneField)
    try:
        bank = emp.bankdetails
    except BankDetails.DoesNotExist:
        bank = None

    # ✅ Family Members (ForeignKey Related Name)
    family_members = emp.family_members.all()
    education_documents = emp.education_documents.all()
    government_documents = emp.government_documents.all()

    # ✅ Salary & Statutory
    statutory, _ = SalaryAndStatutory.objects.get_or_create(
        employee=emp,
        defaults={'salary_amount': 0}
    )
    statutory_form = SalaryAndStatutoryForm(instance=statutory)

    context = {
        'emp': emp,
        'profile': profile,
        'bank': bank,
        'family_members': family_members,
        'emergency_contacts': emergency_contacts,
        'educations': educations,
        'experiences': experiences,
        'salary_form': statutory_form,
        'education_documents': education_documents,
        'government_documents': government_documents,  # ✅ Add this
    }
    return render(request, 'employee/employee_detail_view.html', context)