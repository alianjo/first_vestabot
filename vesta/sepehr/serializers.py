from rest_framework import serializers
from .models import Supplier
import datetime


def validate_date(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y/%m/%d')
    except:
        raise serializers.ValidationError("فرمت تاریخ مشکل دارد, باید به این شکل باشد YYYY/MM/DD")

class PassengersSerializer(serializers.Serializer):
    dplGender_ctl=serializers.CharField(required=True),
    txtPassengerFirstName=serializers.CharField(required=True),
    txtPassengerLastName=serializers.CharField(required=True),
    dplTravelDocumentType=serializers.CharField(required=True),
    dplNationality_ID=serializers.CharField(required=True),
    txtPassenger_PassportNo=serializers.CharField(required=True),
    BirthDay_Day=serializers.CharField(required=True),
    BirthDay_Month=serializers.CharField(required=True),
    BirthDay_Year=serializers.CharField(required=True)

class first_validation(serializers.Serializer):
    """Your data serializer, define your fields here."""
    name_company = serializers.CharField(max_length=300, required=True)
    dplFlightAdults = serializers.IntegerField(required=True)
    dplFlightChilds = serializers.IntegerField(required=True)
    dplFlightInfants = serializers.IntegerField(required=True)
    DepartureFlight = serializers.CharField(max_length=30, required=True)
    AdultPrice = serializers.IntegerField(required=True)
    ChildPrice = serializers.IntegerField(required=True)
    InfantPrice = serializers.IntegerField(required=True)
    dplFrom = serializers.CharField(max_length=10, required=True)
    dplTo = serializers.CharField(max_length=10, required=True)
    txtDepartureDate = serializers.CharField(max_length=10, required=True)
    txtPhone = serializers.CharField(max_length=11, required=True)
    txtReservation_Email = serializers.CharField(max_length=200, required=True)
    txtAddress=serializers.CharField(max_length=450, required=False, allow_blank=True, default='')
    txtRemark=serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    dplMobileCountry=serializers.CharField(max_length=200, required=False)
    passengers = PassengersSerializer(many=True)

    def validate(self, data):
        name_company = data['name_company']
        try:
            Supplier.objects.get(status=True, name=name_company)
        except:
            raise serializers.ValidationError("شرکت پروازی وجود ندارد و یا غیرفعال شده است")
        validate_date(data['txtDepartureDate'])
        count_passengers = data['dplFlightAdults'] + data['dplFlightChilds'] + data['dplFlightInfants']
        len_passengers = len(data['passengers'])
        if len_passengers < count_passengers:
            raise serializers.ValidationError("تعداد مسافرین درخواستی با لیست مسافرین همخوانی ندارد")
        return data

class private_search_validation(serializers.Serializer):
    source = serializers.CharField(max_length=10, required=True)
    destination = serializers.CharField(max_length=10, required=True)
    date = serializers.CharField(max_length=10, required=True)


