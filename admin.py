from omniport.admin.site import omnipotence

from bhawan_app.models import (
    Profile,
    Contact,
    Facility,
    RoomBooking,
    Complaint,
    Timing,
    Visitor,
    Event,
    ComplaintTimeSlot,
    Resident
)

from bhawan_app.models.roles import HostelAdmin

omnipotence.register(Profile)
omnipotence.register(Contact)
omnipotence.register(Facility)
omnipotence.register(RoomBooking)
omnipotence.register(Complaint)
omnipotence.register(HostelAdmin)
omnipotence.register(Timing)
omnipotence.register(Visitor)
omnipotence.register(Event)
omnipotence.register(ComplaintTimeSlot)
omnipotence.register(Resident)

