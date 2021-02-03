import swapper

from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bhawan_app.serializers.personal_info import PersonalInfoSerializer
from bhawan_app.models import Resident, HostelAdmin


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
        resident = None
        admin = None
        try:
            resident = Resident.objects.get(person=person)
        except Resident.DoesNotExist:
            pass
        try:
            admin = HostelAdmin.objects.filter(person=person).first()
        except HostelAdmin.DoesNotExist:
            pass
        if not admin and not resident:
            return Response(
                'You are neither a resident nor an admin !',
                status=status.HTTP_403_FORBIDDEN,
            )
        instance = admin if admin else resident
        serializer = PersonalInfoSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
