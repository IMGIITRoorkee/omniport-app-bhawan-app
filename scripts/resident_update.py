import swapper

from bhawan_app.models.resident import Resident
from base_auth.managers.get_user import get_user
from shell.constants import residences

ResidentialInformation = swapper.load_model('kernel', 'ResidentialInformation')
Student = swapper.load_model('kernel', 'Student')
Residence = swapper.load_model('kernel','Residence')

def update_residents():

    students = Student.objects.all()

    for student in students:
        try:
            resident = Resident.objects.get(person=student.person,is_resident=True)
            _ = ResidentialInformation.objects.update_or_create(
                person=resident.person,
                defaults={
                    'room_number':resident.room_number,
                    'residence':resident.hostel,
                }
            )
        except:
            _ = ResidentialInformation.objects.update_or_create(
                person=student.person,
                defaults={
                    'room_number':'NA',
                    'residence':Residence.objects.get(code=residences.NON_RESIDENT),
                }
            )

    return "Residential Information updated for students."
