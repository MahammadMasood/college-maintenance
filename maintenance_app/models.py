from django.db import models
from django.contrib.auth.models import User
class Profile(models.Model):
    ROLE_CHOICES = (('HOD','Head of Department'),('ADMIN','Principal/Admin'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='HOD')
    branch = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return f"{self.user.username} - {self.role}"
class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [('Pending','Pending'),('Approved','Approved'),('Rejected','Rejected'),('Completed','Completed'),]
    hod = models.ForeignKey(User, on_delete=models.CASCADE)
    branch = models.CharField(max_length=100)
    title = models.CharField(max_length=150)
    lab_name = models.CharField(max_length=100)
    description = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_remark = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.title} ({self.branch}) - {self.status}"
