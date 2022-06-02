from omniport.admin.site import omnipotence

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
    StudentAccommodation
)

from bhawan_app.models.roles import HostelAdmin

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

