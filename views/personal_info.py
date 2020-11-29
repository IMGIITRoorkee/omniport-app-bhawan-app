import swapper

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhawan_app.serializers.personal_info import PersonalInfoSerializer
from bhawan_app.models import Resident, HostelAdmin
# ResidentialInformation = swapper.load_model('Kernel', 'ResidentialInformation')


class PersonalInfoView(generics.RetrieveAPIView):
    """
    This view shows some hostel related personal information of the currently
    logged in user
    """

    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, pk=None):
        """
        View to serve GET requests
        :param request: the request that is to be responded to
        :param args: arguments
        :param kwargs: keyword arguments
        :return: the response for request
        """

        person = request.person
        try:
            resident = Resident.objects.get(person=person)
        except Resident.DoesNotExist:
            try:
                admin = HostelAdmin.objects.get(person=person)
            except HostelAdmin.DoesNotExist:
                return Response(
                    'Please fill in your residential information.',
                    status=status.HTTP_206_PARTIAL_CONTENT,
                )
        instance = resident if resident else admin
        serializer = PersonalInfoSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
