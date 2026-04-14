import swapper

from rest_framework import serializers

from bhawan_app.models import NonResidingStudent


Hostel = swapper.load_model('kernel', 'Residence')


class NonResidingStudentSerializer(serializers.ModelSerializer):
    hostel_code = serializers.CharField(source='hostel.code', read_only=True)
    hostel_name = serializers.CharField(source='hostel.name', read_only=True)

    class Meta:
        model = NonResidingStudent
        fields = [
            'id',
            'hostel',
            'hostel_code',
            'hostel_name',
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
        read_only_fields = ['hostel']

    def validate(self, attrs):
        validated_attrs = super().validate(attrs)

        from_date = validated_attrs.get('from_date', getattr(self.instance, 'from_date', None))
        upto_date = validated_attrs.get('upto_date', getattr(self.instance, 'upto_date', None))

        if from_date and upto_date and from_date >= upto_date:
            raise serializers.ValidationError('From date must be earlier than Upto date')

        return validated_attrs

    def create(self, validated_data):
        hostel_code = self.context.get('hostel__code')
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Hostel.DoesNotExist:
            raise serializers.ValidationError('Wrong hostel code')

        return NonResidingStudent.objects.create(hostel=hostel, **validated_data)
