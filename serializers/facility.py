import swapper

from rest_framework import serializers
from bhawan_app.models import Facility
from bhawan_app.serializers.timing import TimingSerializer

Hostel = swapper.load_model('kernel', 'Residence')


class FacilitySerializer(serializers.ModelSerializer):
    '''
    Serializer for Facility objects
    '''

    timings = TimingSerializer(many=True,)

    class Meta:
        '''
        Meta class for FacilitySerializer
        '''

        model = Facility
        fields = [
            'id',
            'name',
            'description',
            'display_picture',
            'timings',
        ]

    def create(self, validated_data):
        timing_data = validated_data.pop('timings')
        timing_serializer = TimingSerializer(data=timing_data, many=True)
        timing_serializer.is_valid(raise_exception=True)

        hostel_code = self.context['hostel__code']
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Exception:
            raise serializers.ValidationError('Wrong hostel code')

        try:
            facility = Facility.objects.create(**validated_data, hostel=hostel,)
        except Exception:
            raise serializers.ValidationError('Wrong fields for facility.')

        timing_objects = timing_serializer.save()
        facility.timings.add(*timing_objects)

        return facility
    
    def update(self, instance, validated_data):
        if 'timings' in validated_data.keys():
            timings = validated_data.pop('timings')
            timing_serializer = TimingSerializer(data=timings, many=True)
            timing_serializer.is_valid(raise_exception=True)
            timings = timing_serializer.save()
            instance.timings.clear()
            instance.timings.add(*timings)
        return super().update(instance, validated_data)

