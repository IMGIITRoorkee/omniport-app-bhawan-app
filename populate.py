import string
import random
import datetime
import swapper
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "omniport.settings")
django.setup()

from base_auth.models import User

Branch = swapper.load_model('kernel', 'Branch')
Person = swapper.load_model('kernel', 'Person')
Student = swapper.load_model('kernel', 'Student')
FacultyMember = swapper.load_model('kernel', 'FacultyMember')
Maintainer = swapper.load_model('kernel', 'Maintainer')


# Increase the value of n to make more users
n = 5
# For generating unique enrolment numbers
count = 0
# Create a branch from omnipotence
branch_id = Branch.objects.all().first().id

for x in range(n):

    student_user = User()
    student_user_name = f"bhawan_student{x+1}"
    student_user.username = student_user_name
    student_user.set_password("pass")
    student_user.is_superuser = True
    student_user.save()
    person = Person()
    person.user = student_user
    person.full_name = f'bhawan_student{x+1}'
    person.save()
    student = Student()
    student.start_date = datetime.date.today()
    student.person = person
    student.branch_id = branch_id
    student.current_year = 2
    student.current_semester = 4
    student.enrolment_number = 12000000 + count
    count = count + 1
    student.save()

for x in range(n):
    user = User()
    user_name = f"warden{x+1}"
    user.username = user_name
    user.set_password("pass")
    user.is_superuser = True
    user.save()
    person = Person()
    person.user = user
    person.full_name = f'warden{x+1}'
    person.save()

