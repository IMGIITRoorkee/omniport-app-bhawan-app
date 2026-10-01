from omniport.admin.site import omnipotence
from django.contrib import admin

from bhawan_app.models import (
    Profile,
    Contact,
    Facility,
    RoomBooking,
    Complaint,
    Item,
    DefaultItem,
    Timing,
    Visitor,
    Event,
    ComplaintTimeSlot,
    Resident,
    Room,
    StudentAccommodation,
    NonResidingStudent,
)

from bhawan_app.models.roles import HostelAdmin


class NonResidingStudentAdmin(admin.ModelAdmin):
    list_display = (
        'hostel',
        'name',
        'designation',
        'department',
        'mobile_number',
        'room_number',
        'from_date',
        'upto_date',
        'email_id',
    )

omnipotence.register(Profile)
omnipotence.register(Contact)
omnipotence.register(Facility)
omnipotence.register(RoomBooking)
omnipotence.register(Complaint)
omnipotence.register(Item)
omnipotence.register(DefaultItem)
omnipotence.register(HostelAdmin)
omnipotence.register(Timing)
omnipotence.register(Visitor)
omnipotence.register(Event)
omnipotence.register(ComplaintTimeSlot)
omnipotence.register(Resident)
omnipotence.register(Room)
omnipotence.register(StudentAccommodation)
omnipotence.register(NonResidingStudent, NonResidingStudentAdmin)

