"""
Designation of hostel staff at IIT Roorkee
"""

# Administrative council
ASSISTANT_WARDEN = 'aw'
CHIEF_WARDEN = 'cw'
SUPERVISOR = 'sup'
WARDEN = 'war'
WARDEN_WELLNESS = 'waw'
ADMINISTRATIVE_COUNCIL = (
    (ASSISTANT_WARDEN, 'Assistant warden'),
    (CHIEF_WARDEN, 'Chief warden'),
    (SUPERVISOR, 'Supervisor'),
    (WARDEN, 'Warden'),
    (WARDEN_WELLNESS, 'Warden wellness'),
)

# Student council
BHAWAN_SECRETARY = 'bscy'
CULTURAL_SECRETARY = 'cscy'
MAINTENANCE_SECRETARY = 'mscy'
MESS_SECRETARY = 'mescy'
SPORTS_SECRETARY = 'sscy'
TECHNICAL_SECRETARY = 'tscy'
STUDENT_COUNCIL = (
    (BHAWAN_SECRETARY, 'Bhawan secretary'),
    (CULTURAL_SECRETARY, 'Cultural secretary'),
    (MAINTENANCE_SECRETARY, 'Maintenance secretary'),
    (MESS_SECRETARY, 'Mess secretary'),
    (SPORTS_SECRETARY, 'Sports secretary'),
    (TECHNICAL_SECRETARY, 'Technical secretary'),
)

DESIGNATIONS = (
    ADMINISTRATIVE_COUNCIL + STUDENT_COUNCIL
)