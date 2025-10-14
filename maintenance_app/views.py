from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import MaintenanceRequest, Profile
from .forms import MaintenanceRequestForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout


class CustomLoginView(LoginView):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_superuser:
                return redirect('admin_dashboard')
            return redirect('hod_dashboard')
        return super().get(request, *args, **kwargs)

def is_admin(user):
    try:
        return user.profile.role == 'ADMIN'
    except Exception:
        return user.is_superuser
def home_redirect(request):
    if request.user.is_authenticated:
        try:
           if User.is_superuser:
             return redirect('admin_dashboard')
           else:
              return redirect('hod_dashboard')

            
        except Exception:
            return redirect('hod_dashboard')
    return redirect('login')
@login_required
def hod_dashboard(request):
    requests = MaintenanceRequest.objects.filter(hod=request.user).order_by('-date_submitted')
    return render(request, 'hod_dashboard.html', {'requests': requests})
@login_required
def new_request(request):
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            mr = form.save(commit=False)
            mr.hod = request.user
            try:
                if not mr.branch:
                    mr.branch = request.user.profile.branch
            except Exception:
                pass
            mr.save()
            messages.success(request, 'Request submitted successfully.')
            return redirect('hod_dashboard')
    else:
        initial = {}
        try:
            initial['branch'] = request.user.profile.branch
        except Exception:
            pass
        form = MaintenanceRequestForm(initial=initial)
    return render(request, 'new_request.html', {'form': form})
@login_required
def request_detail(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    return render(request, 'request_detail.html', {'req': req})
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    all_requests = MaintenanceRequest.objects.order_by('-date_submitted')
    pending = all_requests.filter(status='Pending')
    return render(request, 'admin_dashboard.html', {'requests': all_requests, 'pending': pending})
@login_required
@user_passes_test(is_admin)
def approve_request(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'Approved'
    req.admin_remark = request.POST.get('admin_remark', 'Approved by admin')
    req.save()
    messages.success(request, 'Request approved.')
    return redirect('admin_dashboard')
@login_required
@user_passes_test(is_admin)
def reject_request(request, pk):
    req = get_object_or_404(MaintenanceRequest, pk=pk)
    req.status = 'Rejected'
    req.admin_remark = request.POST.get('admin_remark', 'Rejected by admin')
    req.save()
    messages.success(request, 'Request rejected.')
    return redirect('admin_dashboard')


def user_logout(request):
    logout(request)
    return redirect('login')
