import swapper

from rest_framework import serializers
from bhawan_app.models import Room

Hostel = swapper.load_model('kernel', 'Residence')


class RoomSerializer(serializers.ModelSerializer):
    '''
    Serializer for Room objects
    '''

    class Meta:
        '''
        Meta class for RoomSerializer
        '''

        model = Room
        fields = [
            'id',
            'hostel',
            'room_type',
            'occupancy',
            'count',
            'datetime_modified',
        ]

    def create(self, validated_data):
    
        hostel_code = self.context['hostel__code']
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Exception:
            raise serializers.ValidationError('Wrong hostel code')

        try:
            room = Room.objects.create(**validated_data, hostel=hostel,)
        except Exception:
            raise serializers.ValidationError('Wrong fields for room.')

        return room


