import swapper

from rest_framework import serializers

from bhawan_app.models import Event
from bhawan_app.serializers.timing import TimingSerializer
from bhawan_app.serializers.resident import ResidentSerializer

Hostel = swapper.load_model("Kernel", "Residence")


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for Facility objects
    """

    timings = TimingSerializer(many=True,)
    registered_students = ResidentSerializer(many=True,)

    class Meta:
        """
        Meta class for FacilitySerializer
        """

        model = Event
        fields = [
            "id",
            "name",
            "date",
            "description",
            "display_picture",
            "timings",
            "registered_students",
            "location",
            "deadline_date",
        ]

    def create(self, validated_data):
        timing_data = validated_data.pop("timings")
        timing_serializer = TimingSerializer(data=timing_data, many=True)
        timing_serializer.is_valid(raise_exception=True)
        registered_students = ResidentSerializer(many=True)

        hostel_code = self.context["hostel__code"]
        try:
            hostel = Hostel.objects.get(code=hostel_code)
        except Exception:
            raise serializers.ValidationError("Wrong hostel code")

        try:
            event = Event.objects.create(**validated_data, hostel=hostel,)
        except Exception:
            raise serializers.ValidationError("Wrong fields for event")

        timing_objects = timing_serializer.save()
        for timing in timing_objects:
            event.timings.add(timing)

        return event

    def update(self, instance, validated_data):
        if 'timings' in validated_data.keys():
            timings = validated_data.pop('timings')
            timing_serializer = TimingSerializer(data=timings, many=True)
            timing_serializer.is_valid(raise_exception=True)
            timings = timing_serializer.save()
            instance.timings.clear()
            instance.timings.add(*timings)
        if 'registered_students' in validated_data.keys():
            students = validated_data.pop('registered_students')
            students_serializer = ResidentSerializer(data=students, many=True)
            students_serializer.is_valid(raise_exception=True)
            students = students_serializer.save()
            instance.students.clear()
            instance.students.add(*students)
        return super().update(instance, validated_data)

        
