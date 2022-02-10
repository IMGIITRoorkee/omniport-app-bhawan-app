from formula_one.models.generics.contact_information import ContactInformation

def get_phone_number(resident):
        """
        Retrives the phone number of a resident
        if he is a student
        """
        try:
            contact_information = \
                ContactInformation.objects.filter(person=resident.person).first()
            if(contact_information):
                return contact_information.primary_phone_number
        except ContactInformation.DoesNotExist:
            return None
        return None