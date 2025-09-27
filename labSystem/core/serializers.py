# from rest_framework.response import Response
# from rest_framework.decorators import api_view
# from rest_framework import status
# from django.shortcuts import get_object_or_404

# from .models import Patient, Appointment
# from .serializers import AppointmentSerializer   # ✅ الاستيراد الصحيح
# from .utils import generate_otp, send_sms


# @api_view(["POST"])
# def book_appointment(request):
#     # 1) التحقق من البيانات الأساسية
#     phone = request.data.get("phone")
#     name = request.data.get("name")

#     if not phone:
#         return Response({"error": "رقم الهاتف مطلوب"}, status=status.HTTP_400_BAD_REQUEST)

#     if not name:
#         return Response({"error": "الاسم مطلوب"}, status=status.HTTP_400_BAD_REQUEST)

#     # 2) إنشاء/تحديث المريض
#     patient, _ = Patient.objects.update_or_create(
#         phone=phone,
#         defaults={"name": name}
#     )

#     # 3) إنشاء موعد بالحالة pending_confirmation
#     appt_data = request.data.copy()
#     appt_data["patient"] = patient.id

#     serializer = AppointmentSerializer(data=appt_data)
#     serializer.is_valid(raise_exception=True)
#     appointment = serializer.save(status="pending_confirmation")

#     # 4) إنشاء OTP
#     otp_code = generate_otp(patient)

#     # 5) إرسال OTP عبر SMS/واتساب (dummy send)
#     send_sms(phone, f"رمز التحقق لحجزك هو: {otp_code}")

#     # 6) الرد للمستخدم
#     return Response(
#         {
#             "message": "تم إنشاء الحجز، الرجاء إدخال رمز OTP لتأكيد الموعد.",
#             "appointment_id": appointment.id
#         },
#         status=status.HTTP_201_CREATED
#     )








from rest_framework import serializers
from .models import Patient, Appointment


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = "__all__"
