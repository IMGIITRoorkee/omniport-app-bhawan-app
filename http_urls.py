from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bhawan_app.views.profile import ProfileViewset
from bhawan_app.views.contact import ContactViewset
from bhawan_app.views.facility import FacilityViewset
from bhawan_app.views.complaint import ComplaintViewset
from bhawan_app.views.item import ItemViewset
from bhawan_app.views.default_item import DefaultItemViewset
from bhawan_app.views.room_booking import RoomBookingViewset
from bhawan_app.views.personal_info import PersonalInfoView
from bhawan_app.views.event import EventViewset
from bhawan_app.views.complaint_time_slot import ComplaintTimeSlotViewset
from bhawan_app.views.hostel_admin import HostelAdminViewset
from bhawan_app.views.constant import ConstantViewset
from bhawan_app.views.resident import ResidentViewset



app_name = "bhawan_app"

router = DefaultRouter()

router.register(
    r"constants", ConstantViewset, basename="constant",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/complaint", ComplaintViewset, basename="complaint",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/item", ItemViewset, basename="item",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/default_item", DefaultItemViewset, basename="default_item",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/room_booking",
    RoomBookingViewset,
    basename="room_booking",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/facility", FacilityViewset, basename="facility",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/profile", ProfileViewset, basename="profle",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/contact", ContactViewset, basename="contact",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/event", EventViewset, basename="event",
),
router.register(
    r"(?P<hostel__code>[\w\-]+)/resident", ResidentViewset, basename="resident",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/time_slot",
    ComplaintTimeSlotViewset,
    basename="time_slot",
)
router.register(
    r"(?P<hostel__code>[\w\-]+)/admin", HostelAdminViewset, basename="admin",
)

urlpatterns = [
    path(
        'personal_info/',
        PersonalInfoView.as_view(),
        name='personal_info',
    ),
]


urlpatterns += router.urls
