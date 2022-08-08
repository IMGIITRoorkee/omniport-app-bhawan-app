from asyncore import read
import swapper
import csv
import pandas as pd
import io

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponse
from datetime import datetime

from bhawan_app.models import Resident
from bhawan_app.serializers.student_accommodation import StudentAccommodationSerializer
from bhawan_app.managers.services import is_senior_maintainer

Person = swapper.load_model('kernel', 'Person')
Residence = swapper.load_model('kernel', 'Residence')

class UploadBhawanDataViewset(viewsets.ModelViewSet):
    """
    View for uploading/updating student information for a particular bhawan
    """

    serializer_class = StudentAccommodationSerializer
    permission_classes = [IsAuthenticated,]
    allowed_methods = ['PATCH']
    pagination_class = None

    @action(detail=False, methods=['patch'])
    def update_data(self, request, hostel__code):
        """
        This method gets a csv with details of accomodation
        in a particular bhawan and updates the database.
        """
        
        if not is_senior_maintainer(request.person):
            return Response("You are not allowed to perform this action !",
            status=status.HTTP_403_FORBIDDEN,
            )

        data = request.data
        csv_file = data.get('csv_file')
        if not hostel__code:
            return Response("Bhawan Code not provided !",
                status=status.HTTP_404_NOT_FOUND,
            )
        if not csv_file:
            return Response(
                "No CSV file provided !",
                status=status.HTTP_404_NOT_FOUND,
            )
        ROOM_NA = ['', 'Not Joined', 'Not joined yet', 'NOT ALLOWTED', 'Pending', 'Not Joining yet', 'not joined yet', 'Not Joined Yet']
 
        try:
            hostel = Residence.objects.get(code=hostel__code)
            file = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(file))
            header = False
            for student_data in csv_reader:
                if not header:
                    header = True
                    continue
                else:
                    student_enrollement_no = student_data[1]
                    room_no = student_data[7]
                    in_campus = student_data[11]
                    fee_status = student_data[10]
                    start_date = student_data[12].split('/r/n')[0]
                    try:
                        person = Person.objects.get(student__enrolment_number=student_enrollement_no)
                    except:
                        return Response(
                            f'Student not found {student_enrollement_no} !',
                            status=status.HTTP_404_NOT_FOUND,
                        )
                    if room_no.strip() in ROOM_NA:
                        room_no = "NA"

                    in_campus = (in_campus.strip()).lower()
                    is_living_in_campus = True
                    if in_campus == "no":
                        is_living_in_campus = False
                    elif in_campus == "yes":
                        is_living_in_campus = True

                    fee_status = (fee_status.strip()).lower()
                    fee_type = "liv"
                    if fee_status == "liv. in campus":
                        fee_type = "liv"
                    elif fee_status == "not liv. in campus":
                        fee_type = "nlv"
                    elif fee_status == "nd":
                        fee_type = "nd"

                    start_date_format = start_date
                    if start_date != "":
                        valid_date = False
                        start_date = start_date.strip()
                        for fmt in ('%d-%m-%y', '%d.%m.%Y', '%d/%m/%Y', '%d.%m-%y', '%d-%m.%y'):
                            try:
                                valid_date = True
                                start_date_format = datetime.strptime(start_date, fmt)
                            except ValueError:
                                pass
                        if not valid_date:
                            return Response(
                                f'Start Date not found for {student_data[1]} !',
                                status=status.HTTP_404_NOT_FOUND,
                            )
                    
                    try:
                        Resident.objects.update_or_create(
                            person = person,
                            is_resident = True,
                            defaults = {
                                'person': person,
                                'room_number': room_no,
                                'hostel': hostel,
                                'is_living_in_campus': is_living_in_campus,
                                'fee_type': fee_type,
                                'start_date': start_date_format
                            }
                        )
                    except Exception as e:
                        return Response(f'Exception {e} for {student_data[1]}\n')
        except:
            return Response(
                "Incorrect bhawan Code/ Cannot read csv file !",
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            "Bhawan data updated",
            status=status.HTTP_200_OK,
        )
