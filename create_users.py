# Run this AFTER you run: python manage.py migrate
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_maintenance.settings')
django.setup()
from django.contrib.auth.models import User
from maintenance_app.models import Profile
def create_user(username, password, first_name='', role='HOD', branch=None, is_super=False):
    if User.objects.filter(username=username).exists():
        print('User exists:', username)
        return User.objects.get(username=username)
    u = User.objects.create_user(username=username, password=password, first_name=first_name)
    if is_super:
        u.is_staff = True
        u.is_superuser = True
        u.save()
    profile = Profile.objects.create(user=u, role=('ADMIN' if role=='ADMIN' else 'HOD'), branch=branch if branch else 'General')
    print('Created user', username, 'role', profile.role)
    return u
# Principal (admin)
create_user('principal', 'Principal@123', first_name='Principal', role='ADMIN', is_super=True)
# 6 HODs
create_user('hod_cse', 'HodCse@123', first_name='HOD_CSE', role='HOD', branch='CSE')
create_user('hod_ece', 'HodEce@123', first_name='HOD_ECE', role='HOD', branch='ECE')
create_user('hod_mech', 'HodMech@123', first_name='HOD_MECH', role='HOD', branch='MECH')
create_user('hod_civil', 'HodCivil@123', first_name='HOD_CIVIL', role='HOD', branch='CIVIL')
create_user('hod_eee', 'HodEee@123', first_name='HOD_EEE', role='HOD', branch='EEE')
create_user('hod_it', 'HodIt@123', first_name='HOD_IT', role='HOD', branch='IT')
print('All users created (if migrations applied).')
