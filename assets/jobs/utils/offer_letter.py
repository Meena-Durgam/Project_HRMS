# jobs/utils/offer_letter.py

from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
import io
from ..models import OfferLetter

def generate_offer_letter(application):
    if application.status != 'hired':
        return None

    # Prevent duplicate generation
    if hasattr(application, 'offer_letter'):
        return application.offer_letter

    job = application.job
    applicant = application.applicant
    company = job.company
    department = job.department

    # Render HTML
    html_content = render_to_string('offer_letter_pdf.html', {
        'applicant_name': applicant.name,
        'job_title': job.title,
        'company_name': company.name,
        'department': department.name if department else '',
        'salary': job.salary_to,
        'start_date': job.start_date,
    })

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html_content, dest=result)  # ✅ FIXED

    if pisa_status.err:
        print("❌ PDF generation failed with xhtml2pdf")
        return None

    # Save OfferLetter record and attach PDF
    offer = OfferLetter.objects.create(
        application=application,
        applicant_name=applicant.name,
        job_title=job.title,
        company_name=company.name,
        department=department.name if department else '',
        salary=job.salary_to,
        start_date=job.start_date,
    )

    filename = f"offer_letter_{offer.id}.pdf"
    offer.pdf.save(filename, ContentFile(result.getvalue()))
    offer.save()

    return offer
