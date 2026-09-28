import swapper

from rest_framework import serializers

from bhawan_app.constants import statuses

Student = swapper.load_model('kernel', 'Student')
Residence = swapper.load_model('kernel', 'Residence')


class BulkRegisterRowSerializer(serializers.Serializer):
    """
    Validates one row of a bulk resident registration, with empty values left out
    """

    enrolment_number = serializers.CharField(
        validators=Student._meta.get_field('enrolment_number').validators,
    )
    hostel_code = serializers.SlugRelatedField(
        slug_field='code',
        queryset=Residence.objects.all(),
        source='hostel',
    )
    room_no = serializers.CharField()
    seat = serializers.CharField(required=False)
    fee_type = serializers.ChoiceField(choices=statuses.FEE_TYPES, required=False)
    admission_date = serializers.DateField(required=False)
    mobile_no = serializers.CharField(max_length=15, required=False)
    address = serializers.CharField(required=False)
    father_name = serializers.CharField(max_length=255, required=False)
    father_contact = serializers.CharField(max_length=15, required=False)
    mother_name = serializers.CharField(max_length=255, required=False)
    mother_contact = serializers.CharField(max_length=15, required=False)
