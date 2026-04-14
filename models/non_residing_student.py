import swapper

from django.db import models

from formula_one.models.base import Model


class NonResidingStudent(Model):
    """Stores non-dining, non-residing student registrations for a bhawan."""

    RA = 'ra'
    PDF = 'pdf'
    JRF = 'jrf'
    SRF = 'srf'
    PROJECT_FELLOW = 'project_fellow'
    NPDF = 'npdf'
    IPDF = 'ipdf'
    RESEARCH_INTERN = 'research_intern'
    VISITOR = 'visitor'

    DESIGNATIONS = (
        (RA, 'RA'),
        (PDF, 'PDF'),
        (JRF, 'JRF'),
        (SRF, 'SRF'),
        (PROJECT_FELLOW, 'Project Fellow'),
        (NPDF, 'NPDF'),
        (IPDF, 'IPDF'),
        (RESEARCH_INTERN, 'Research Intern'),
        (VISITOR, 'Visitor'),
    )

    hostel = models.ForeignKey(
        to=swapper.get_model_name('kernel', 'Residence'),
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=20, choices=DESIGNATIONS)
    department = models.CharField(max_length=255, blank=True, default='')
    mobile_number = models.CharField(max_length=20)
    room_number = models.CharField(max_length=20)
    from_date = models.DateField()
    upto_date = models.DateField()
    email_id = models.EmailField()

    class Meta:
        ordering = ['-from_date', '-datetime_created']

    def __str__(self):
        return f"{self.name} ({self.hostel.code})"
