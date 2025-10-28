
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import MaintenanceRequest, Profile
from .forms import MaintenanceRequestForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
import json
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage
import tempfile
import os
from weasyprint import HTML
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.views.decorators.cache import never_cache



class CustomLoginView(LoginView):
    template_name = 'registration/login.html'  # Path confirmed

    def form_valid(self, form):
        """Called when valid form data has been POSTed."""
        # Log the user in
        response = super().form_valid(form)

        # Role-based redirect
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'PRINCIPAL'):
            return redirect('admin_dashboard')
        return redirect('hod_dashboard')

    def get(self, request, *args, **kwargs):
        """Redirect authenticated users away from the login page."""
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        """Default success URL after login."""
        user = self.request.user
        if user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'PRINCIPAL'):
            return reverse('admin_dashboard')
        return reverse('hod_dashboard')
 
def is_admin(user): 
    try:
        # Allow both ADMIN and PRINCIPAL roles
        return user.profile.role in ['ADMIN', 'PRINCIPAL']
    except Exception:
        # Fallback for users without profile (like superuser)
        return user.is_superuser


def home_redirect(request):
    if request.user.is_authenticated:
        try:
            if request.user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(request.user, 'username') and request.user.username == 'prinipal':
                return redirect('admin_dashboard')
            else:
                return redirect('hod_dashboard')
        except Exception:
            return redirect('hod_dashboard')

    return render(request, 'homepage.html')


@never_cache
@login_required
def hod_dashboard(request):
    # Base queryset (only this HOD’s requests)
    requests = MaintenanceRequest.objects.filter(hod=request.user).order_by('-date_submitted')

    # Capture optional ?status= parameter
    status_filter = request.GET.get("status")

    if status_filter:
        requests = requests.filter(status=status_filter)

    # Summary counts for cards
    total = requests.count() if not status_filter else MaintenanceRequest.objects.filter(hod=request.user).count()
    pending = MaintenanceRequest.objects.filter(hod=request.user, status="Pending").count()
    approved = MaintenanceRequest.objects.filter(hod=request.user, status="Approved").count()
    rejected = MaintenanceRequest.objects.filter(hod=request.user, status="Rejected").count()

    context = {
        "requests": requests,
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "status_filter": status_filter,
    }

    return render(request, "hod_dashboard.html", context)

@login_required
def new_request(request):
    items = [
        {"device": "SSD", "brand": "Any", "size": "256GB", "price": 1750, "usage": "win-10", "remarks": "best and less price"},
        {"device": "RAM", "brand": "Any", "size": "8GB ddr3", "price": 1600, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "G41-LGA 775 Socket", "price": 1800, "usage": "win-7", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "H61-LGA 1155 Socket", "price": 2100, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "H110-LGA 1151 Socket", "price": 2100, "usage": "win-11", "remarks": "best and less price"},
        {"device": "Processor", "brand": "i3 3rd gen", "size": "any", "price": 1200, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Processor", "brand": "Intel dual core", "size": "any", "price": 1000, "usage": "win-10", "remarks": "best and less price"},
        {"device": "SMPS", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Keyboard", "brand": "Any", "size": "any", "price": 700, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Mouse", "brand": "Any", "size": "any", "price": 400, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Keyboard-Mouse combo", "brand": "Any", "size": "any", "price": 1000, "usage": "win-10", "remarks": "best and less price"},
        {"device": "USB to PS2 Connector", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "USB to LAN Connector", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Monitor", "brand": "Any", "size": "any", "price": 5600, "usage": "win-11", "remarks": "best and less price"},
        {"device": "One Set (i3)", "brand": "G61 + H61", "size": "SSD 256GB + RAM 8GB", "price": 7200, "usage": "-", "remarks": "Souza's Price 7200"},
        {"device": "One Set (i5)", "brand": "Gh110", "size": "SSD 256GB + RAM 8GB ddr4", "price": 8800, "usage": "-", "remarks": "Souza's Price 8800"},
        {"device": "One Set (Dual core)", "brand": "G41", "size": "SSD 256GB + RAM 8GB", "price": 6500, "usage": "-", "remarks": "Souza's Price"},
    ]

    if request.method == 'POST':
        branch = request.POST.get('branch')
        title = request.POST.get('title')
        description = request.POST.get('description')
        selected_items = request.POST.get('selected_items')  
        total_amount = request.POST.get('total_amount')

        # Create the request
        mr = MaintenanceRequest(
            title=title,
            description=description,
            branch=branch,
            hod=request.user,
            selected_items=selected_items,
            total_amount=total_amount or 0
        )

        # Set branch if not provided
        try:
            if not mr.branch:
                mr.branch = request.user.profile.branch
        except Exception:
            pass

        mr.save()

        # ------------------- Send Email ------------------- #
        # Get admins and principals
        admins = User.objects.filter(is_superuser=True)
        principals = User.objects.filter(username__iexact='principal')
        recipients = list(admins) + list(principals)
        recipient_emails = [u.email for u in recipients if u.email]

        if recipient_emails:
            subject = f'New Maintenance Request Submitted: {mr.title}'
            link = f'http://yourdomain.com/request/{mr.pk}/'  # replace with your domain

            # Render HTML email template
            html_content = render_to_string('emails/new_request.html', {
                'req': mr,
                'user': request.user,
                'link': link
            })

            msg = EmailMultiAlternatives(subject, '', 'no-reply@yourdomain.com', recipient_emails)
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        # -------------------------------------------------- #

        messages.success(request, 'Request submitted successfully.')
        return redirect('hod_dashboard')

    return render(request, 'new_request.html', {'items': items})


@login_required
def request_detail(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)

    # Decode selected_items JSON if available
    items = []
    if req.selected_items:
        try:
            items = json.loads(req.selected_items)
            # Handle double-encoded JSON (string inside string)
            if isinstance(items, str):
                items = json.loads(items)
        except (json.JSONDecodeError, TypeError):
            items = []

    return render(request, 'request_detail.html', {
        'req': req,
        'items': items,  # ✅ matches your template variable
    })

@never_cache
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    status_filter = request.GET.get('status')
    department_filter = request.GET.get('department')

    requests_qs = MaintenanceRequest.objects.order_by('-date_submitted')

    # Apply filters
    if status_filter:
        requests_qs = requests_qs.filter(status=status_filter)

    if department_filter:
        requests_qs = requests_qs.filter(branch=department_filter)

    # Counts for cards
    total = MaintenanceRequest.objects.count()
    pending = MaintenanceRequest.objects.filter(status='Pending').count()
    approved = MaintenanceRequest.objects.filter(status='Approved').count()
    rejected = MaintenanceRequest.objects.filter(status='Rejected').count()

    # Distinct departments for dropdown
    departments = MaintenanceRequest.objects.values_list('branch', flat=True).distinct()

    context = {
        'requests': requests_qs,
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'departments': departments,
        'status_filter': status_filter,
        'department_filter': department_filter,
    }
    return render(request, 'admin_dashboard.html', context)




@login_required
@user_passes_test(is_admin)
def approve_request(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'Approved'
    req.admin_remark = request.POST.get('admin_remark', 'Approved by admin')
    req.save()

    # Load selected equipment
    items = []
    if req.selected_items:
        try:
            items = json.loads(req.selected_items)
            if isinstance(items, str):
                items = json.loads(items)
        except (json.JSONDecodeError, TypeError):
            items = []

    # Send email
    hod_email = req.hod.email
    if hod_email:
        html_content = render_to_string('request_letter.html', {'request_obj': req, 'items': items})

        # ✅ Safely create and close temp PDF file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            HTML(string=html_content).write_pdf(temp_file.name)
            pdf_path = temp_file.name

        subject = f"Maintenance Request Approved: {req.title}"
        message = (
            f"Dear {req.hod.first_name or req.hod.username},\n\n"
            f"Your maintenance request titled '{req.title}' for branch {req.branch} "
            f"has been approved.\n\n"
            f"Total Amount: ₹{req.total_amount}\n\n"
            f"The detailed request letter (with equipment list) is attached as a PDF.\n\n"
            f"Thank you,\nAdmin Team"
        )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.EMAIL_HOST_USER,
            to=[hod_email],
        )

        # ✅ Reopen PDF to attach after it’s closed
        with open(pdf_path, 'rb') as f:
            email.attach('RequestLetter.pdf', f.read(), 'application/pdf')

        email.send()

        # ✅ Delete temp file after sending
        os.remove(pdf_path)

    messages.success(request, 'Request approved and letter (with equipment) sent as PDF.')
    return redirect('admin_dashboard')
@login_required
@user_passes_test(is_admin)
def reject_request(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'Rejected'
    req.admin_remark = request.POST.get('admin_remark', 'Rejected by admin')
    req.save()

    # Send simple rejection email (no PDF letter)
    hod_email = req.hod.email
    if hod_email:
        subject = f"Maintenance Request Rejected: {req.title}"
        message = (
            f"Dear {req.hod.first_name or req.hod.username},\n\n"
            f"Your maintenance request titled '{req.title}' for branch {req.branch} "
            f"has been rejected.\n\n"
            f"Admin Remark: {req.admin_remark}\n\n"
            f"Total Amount: ₹{req.total_amount}\n\n"
            f"Thank you,\nAdmin Team"
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [hod_email])

    messages.success(request, 'Request rejected and email notification sent .')
    return redirect('admin_dashboard')



@login_required
@user_passes_test(is_admin)
def edit_request(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)

    # equipment list (same as new_request)
    items = [
        {"device": "SSD", "brand": "Any", "size": "256GB", "price": 1750, "usage": "win-10", "remarks": "best and less price"},
        {"device": "RAM", "brand": "Any", "size": "8GB ddr3", "price": 1600, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "G41-LGA 775 Socket", "price": 1800, "usage": "win-7", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "H61-LGA 1155 Socket", "price": 2100, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Motherboard", "brand": "Any", "size": "H110-LGA 1151 Socket", "price": 2100, "usage": "win-11", "remarks": "best and less price"},
        {"device": "Processor", "brand": "i3 3rd gen", "size": "any", "price": 1200, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Processor", "brand": "Intel dual core", "size": "any", "price": 1000, "usage": "win-10", "remarks": "best and less price"},
        {"device": "SMPS", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Keyboard", "brand": "Any", "size": "any", "price": 700, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Mouse", "brand": "Any", "size": "any", "price": 400, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Keyboard-Mouse combo", "brand": "Any", "size": "any", "price": 1000, "usage": "win-10", "remarks": "best and less price"},
        {"device": "USB to PS2 Connector", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "USB to LAN Connector", "brand": "Any", "size": "any", "price": 650, "usage": "win-10", "remarks": "best and less price"},
        {"device": "Monitor", "brand": "Any", "size": "any", "price": 5600, "usage": "win-11", "remarks": "best and less price"},
        {"device": "One Set (i3)", "brand": "G61 + H61", "size": "SSD 256GB + RAM 8GB", "price": 7200, "usage": "-", "remarks": "Souza's Price 7200"},
        {"device": "One Set (i5)", "brand": "Gh110", "size": "SSD 256GB + RAM 8GB ddr4", "price": 8800, "usage": "-", "remarks": "Souza's Price 8800"},
        {"device": "One Set (Dual core)", "brand": "G41", "size": "SSD 256GB + RAM 8GB", "price": 6500, "usage": "-", "remarks": "Souza's Price"},
    ]

    if request.method == 'POST':
        # Update basic fields
        req.branch = request.POST.get('branch', req.branch)
        req.title = request.POST.get('title', req.title)
        req.lab_name = request.POST.get('lab_name', req.lab_name)
        req.description = request.POST.get('description', req.description)

        # Handle selected items JSON
        sel_items = request.POST.get('selected_items', '')
        total_amount = request.POST.get('total_amount', '0')

        try:
            if sel_items:
                json.loads(sel_items)  # Validate JSON
                req.selected_items = sel_items
            else:
                req.selected_items = None
        except json.JSONDecodeError:
            messages.error(request, "Invalid equipment data. Items not saved.")
            return redirect('request_detail', pk=req.pk)

        # Assign total
        try:
            req.total_amount = float(total_amount)
        except ValueError:
            req.total_amount = 0.0

        req.save()
        messages.success(request, "Request updated successfully.")
        return redirect('admin_dashboard')

    # For GET request → Preload selected items for display
    selected_data = {}
    if req.selected_items:
        try:
            selected_items = json.loads(req.selected_items)
            # Use a unique key to differentiate same devices (like multiple Motherboards)
            for item in selected_items:
                key = f"{item.get('device')}_{item.get('size')}"
                selected_data[key] = item.get('quantity', 0)
        except (json.JSONDecodeError, TypeError):
            selected_data = {}

    return render(request, 'edit_request.html', {
        'req': req,
        'items': items,
        'selected_data': selected_data,
    })

def user_logout(request):
    logout(request)
    return redirect('home_redirect') 
