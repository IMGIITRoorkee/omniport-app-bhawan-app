import swapper

from bhawan_app.models.resident import Resident
from base_auth.managers.get_user import get_user

ResidentialInformation = swapper.load_model('kernel', 'ResidentialInformation')

def update_residents(list=[]):

    resident_list = []
    invalid_erns = []

    if len(list) == 0:
        resident_list = Resident.objects.all()
    else:
        for ern in list:
            try:
                resident_list.append(Resident.objects.get(person=get_user(ern).person,is_resident=True))
            except:
                invalid_erns.append(ern)


    for resident in resident_list:
        _ = ResidentialInformation.objects.update_or_create(
                person=resident.person,
                defaults={
                    'room_number':resident.room_number,
                    'residence':resident.hostel,
                }
            )

    return "Following enrollements are either invalid or non residents:",invalid_erns,"Other resident info updated."
