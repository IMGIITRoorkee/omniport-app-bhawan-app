import swapper

from rest_framework import serializers
from bhawan_app.models import StudentAccommodation

Hostel = swapper.load_model('kernel', 'Residence')


class StudentAccommodationSerializer(serializers.ModelSerializer):
    '''
    Serializer for StudentAccommodation objects
    '''

    class Meta:
        '''
        Meta class for StudentAccommodationSerializer
        '''

        model = StudentAccommodation
        fields = [
            'id',
            'hostel',
            'residing_in_single',
            'residing_in_double',
            'residing_in_triple',
            'total_need_accommodation'
        ]

    def create(self, validated_data):
    
        hostel_code = self.context['hostel__code']
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Exception:
            raise serializers.ValidationError('Wrong hostel code')

        try:
            student_accommodation = StudentAccommodation.objects.create(**validated_data, hostel=hostel,)
        except Exception:
            raise serializers.ValidationError('Wrong fields for Student Accommodation')

        return student_accommodation


