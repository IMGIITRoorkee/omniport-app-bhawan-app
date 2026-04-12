import swapper

from rest_framework import serializers

from bhawan_app.models import NonResidingStudent


Hostel = swapper.load_model('kernel', 'Residence')


class NonResidingStudentSerializer(serializers.ModelSerializer):
    hostel_code = serializers.CharField(source='hostel.code', read_only=True)
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)
    staying_hostel_code = serializers.CharField(write_only=True, required=False, allow_blank=True)
    staying_hostel_code_display = serializers.CharField(source='staying_hostel.code', read_only=True)
    staying_hostel_name = serializers.CharField(source='staying_hostel.name', read_only=True)

    class Meta:
        model = NonResidingStudent
        fields = [
            'id',
            'hostel',
            'hostel_code',
            'hostel_name',
            'staying_hostel',
            'staying_hostel_code',
            'staying_hostel_code_display',
            'staying_hostel_name',
            'name',
            'designation',
            'department',
            'mobile_number',
            'room_number',
            'from_date',
            'upto_date',
            'email_id',
            'datetime_created',
            'datetime_modified',
        ]
        read_only_fields = ['hostel', 'staying_hostel']

    def create(self, validated_data):
        hostel_code = self.context.get('hostel__code')
        staying_hostel_code = validated_data.pop('staying_hostel_code', '')
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Hostel.DoesNotExist:
            raise serializers.ValidationError('Wrong hostel code')

        staying_hostel = hostel
        if staying_hostel_code:
            try:
                staying_hostel = Hostel.objects.get(code=staying_hostel_code)
            except Hostel.DoesNotExist:
                raise serializers.ValidationError('Wrong staying hostel code')

        return NonResidingStudent.objects.create(hostel=hostel, staying_hostel=staying_hostel, **validated_data)

    def update(self, instance, validated_data):
        staying_hostel_code = validated_data.pop('staying_hostel_code', None)
        if staying_hostel_code is not None:
            if staying_hostel_code == '':
                instance.staying_hostel = instance.hostel
            else:
                try:
                    instance.staying_hostel = Hostel.objects.get(code=staying_hostel_code)
                except Hostel.DoesNotExist:
                    raise serializers.ValidationError('Wrong staying hostel code')

        return super().update(instance, validated_data)
