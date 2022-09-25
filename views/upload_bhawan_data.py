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
        invalid_data = {
            'Student enrollment no': [],
            'Error while uploading':[]
        }
        try:
            hostel = Residence.objects.get(code=hostel__code)
        except:
            return Response(
                "Incorrect bhawan Code",
                status=status.HTTP_404_NOT_FOUND,
            )
        prev_residents = Resident.objects.filter(hostel=hostel,is_resident=True)
        try:
            file = csv_file.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(file))
        except:
            return Response(
                "Cannot read file !",
                status=status.HTTP_404_NOT_FOUND,
            )
        header = False
        present_residents = Resident.objects.none()
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
                    present_residents |= Resident.objects.filter(person=person,hostel=hostel)
                except:
                    invalid_data['Student enrollment no'].append(student_enrollement_no)
                    invalid_data['Error while uploading'].append('Student not found')
                    continue

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

                if start_date == "":
                    invalid_data['Student enrollment no'].append(student_enrollement_no)
                    invalid_data['Error while uploading'].append('Start date not found')
                    continue

                for character in ['/','-']:
                    start_date = start_date.replace(character,'.')

                start_date_format = start_date
                valid_date = False

                for fmt in ['%d.%m.%Y', '%d.%m.%y']:
                    try:
                        start_date_format = datetime.strptime(start_date, fmt)
                        valid_date = True
                    except:
                        pass

                if not valid_date :
                    invalid_data['Student enrollment no'].append(student_enrollement_no)
                    invalid_data['Error while uploading'].append('Invalid start date format')
                    continue

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
                            'start_date': start_date_format,
                        }
                    )
                except Exception as e:
                    invalid_data['Student enrollment no'].append(student_enrollement_no)
                    invalid_data['Error while uploading'].append('Unable to update data')
                    continue
        prev_residents = set(prev_residents).difference(set(present_residents))
        for resident in prev_residents:
            resident_obj = Resident.objects.get(id=resident.id)
            resident_obj.end_date = datetime.now()
            resident_obj.is_resident = False
            resident_obj.save()
        invalid_data['Student enrollment no'].append('')
        invalid_data['Error while uploading'].append('')
        invalid_data['Student enrollment no'].append("Bhawan data for students other than above mentioned(possibly none) updated.")
        invalid_data['Error while uploading'].append('')
        file_name = 'Errors.csv'
        df = pd.DataFrame(invalid_data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        df.to_csv(path_or_buf=response, index=False)
        return response
