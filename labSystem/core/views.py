from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, Patient, OTP, Result
from .utils import generate_otp, send_sms, generate_secure_link
from datetime import datetime



# ------------------------------
# 1️⃣ صفحة البداية - عرض كل المواعيد
# ------------------------------
def home(request):
    appointments = Appointment.objects.all().order_by('-date_time')
    return render(request, 'core/home.html', {'appointments': appointments})


# ------------------------------
# 2️⃣ حجز موعد جديد + توليد OTP
# ------------------------------
def book_appointment_view(request):
    if request.method == "POST":
        # بيانات المريض
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        patient, _ = Patient.objects.update_or_create(
            phone=phone, defaults={'name': name}
        )

        # بيانات الموعد
        test_type = request.POST.get("test_type")
        date_time_str = request.POST.get("date_time")
        if date_time_str:
            # تحويل النص من datetime-local إلى datetime
            date_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M")
        else:
            date_time = None

        location = request.POST.get("location")
        address = request.POST.get("address", "")

        # طباعة لتأكيد ما استقبل الـ view
        print("Name:", name)
        print("Phone:", phone)
        print("Test type:", test_type)
        print("Date/time:", date_time)
        print("Location:", location)
        print("Address:", address)

        # إنشاء الموعد
        appointment = Appointment.objects.create(
            patient=patient,
            test_type=test_type,
            date_time=date_time,
            location=location,
            address=address,
            status='pending_confirmation'
        )

        # توليد OTP وإرسال رسالة
        otp_code = generate_otp(patient)
        send_sms(
            phone,
            f"رمز التحقق لحجزك هو: {otp_code}\nيرجى إدخاله لتأكيد الموعد."
        )

        return redirect('confirm-otp', appointment_id=appointment.id)

    return render(request, 'core/book_appointment.html')

# ------------------------------
# 3️⃣ تأكيد OTP وتفعيل الموعد
# ------------------------------
def confirm_otp_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.method == "POST":
        otp_input = request.POST.get("otp")
        if appointment.patient.check_otp(otp_input):
            appointment.status = "confirmed"
            appointment.save()
            appointment.patient.otp_set.filter(code=otp_input).delete()

            instructions = "يرجى الصيام 8 ساعات قبل الفحص." if appointment.test_type else ""
            send_sms(
                appointment.patient.phone,
                f"تم تأكيد موعدك بتاريخ {appointment.date_time}. {instructions}"
            )

            return render(request, "core/success.html", {
                "appointment": appointment,
                "message": "تم تأكيد الموعد بنجاح ✅"
            })
        else:
            return render(request, "core/confirm.html", {
                "appointment": appointment,
                "error": "الرمز غير صحيح أو منتهي ❌"
            })

    return render(request, "core/confirm.html", {"appointment": appointment})


# ------------------------------
# 4️⃣ Check-in عند وصول المريض
# ------------------------------
def check_in_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == "POST":
        appointment.status = "checked_in"
        appointment.save()
        # طباعة باركود / ملصق يمكن إضافتها هنا
        return render(request, "core/success.html", {
            "appointment": appointment,
            "message": "تم تسجيل حضور المريض ✅"
        })
    return render(request, "core/check_in.html", {"appointment": appointment})


# ------------------------------
# 5️⃣ رفع واعتماد النتيجة
# ------------------------------
def upload_result_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == "POST" and request.FILES.get("pdf"):
        pdf_file = request.FILES["pdf"]
        result, created = Result.objects.update_or_create(
            appointment=appointment,
            defaults={"pdf": pdf_file, "published": False}
        )
        return render(request, "core/success.html", {
            "appointment": appointment,
            "message": "تم رفع النتيجة بنجاح ✅"
        })
    return render(request, "core/upload_result.html", {"appointment": appointment})


def approve_result_view(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    result.published = True
    result.approved_by = request.user.username if request.user.is_authenticated else "Admin"
    result.save()

    # إرسال رابط آمن للمريض
    secure_link = generate_secure_link(result)
    send_sms(
        result.appointment.patient.phone,
        f"نتيجتك جاهزة للمشاهدة. افتح الرابط الآمن: {secure_link}"
    )

    return render(request, "core/success.html", {
        "appointment": result.appointment,
        "message": "تم اعتماد النتيجة وإرسال الرابط ✅"
    })


# ------------------------------
# 6️⃣ تذكيرات المواعيد
# ------------------------------
def send_reminders():
    now = timezone.now()

    # قبل يوم
    day_before = now + timedelta(days=1)
    appointments_day = Appointment.objects.filter(
        status='confirmed',
        date_time__date=day_before.date()
    )
    for appt in appointments_day:
        instructions = "يرجى الصيام 8 ساعات قبل الفحص." if appt.test_type else ""
        send_sms(
            appt.patient.phone,
            f"تذكير بموعدك غداً الساعة {appt.date_time.strftime('%H:%M')}. {instructions}"
        )

    # قبل ساعتين
    two_hours_before = now + timedelta(hours=2)
    appointments_two_hours = Appointment.objects.filter(
        status='confirmed',
        date_time__gte=two_hours_before - timedelta(minutes=1),
        date_time__lte=two_hours_before + timedelta(minutes=1)
    )
    for appt in appointments_two_hours:
        send_sms(
            appt.patient.phone,
            f"تذكير قصير: موعدك بعد ساعتين الساعة {appt.date_time.strftime('%H:%M')}. افتح الخريطة للوصول."
        )


# ------------------------------
# 7️⃣ متابعة حالات عدم الحضور (No-Show)
# ------------------------------
def check_no_show():
    now = timezone.now()
    window = timedelta(minutes=60)
    pending_appointments = Appointment.objects.filter(
        status='confirmed',
        date_time__lt=now - window
    )
    for appt in pending_appointments:
        appt.status = 'no_show'
        appt.save()
        send_sms(
            appt.patient.phone,
            "لم تحضر لموعدك، يمكنك إعادة الحجز من الرابط: https://lab.com/reschedule"
        )
