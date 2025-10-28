from django.urls import path
from django.contrib.auth import views as auth_views
from maintenance_app.views import CustomLoginView

from . import views
urlpatterns = [ 
    path('accounts/login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('', views.home_redirect, name='home_redirect'),
    path('hod/dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('hod/request/new/', views.new_request, name='new_request'),
    path('request/<int:pk>/', views.request_detail, name='request_detail'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('request/<int:pk>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:pk>/reject/', views.reject_request, name='reject_request'),
    path('request/<int:pk>/edit/',views.edit_request, name='edit_request'),
]
 