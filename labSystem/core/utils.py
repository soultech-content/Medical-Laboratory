import random
from datetime import timedelta
from django.utils import timezone
from .models import OTP

import uuid
from django.utils import timezone
from datetime import timedelta
from .models import Result

# توليد رابط آمن لكل نتيجة
def generate_secure_link(result: Result):
    """
    يولد رابط مؤقت لمشاهدة النتيجة.
    يمكن إضافة تحقق OTP عند الدخول.
    """
    token = uuid.uuid4().hex  # رمز فريد
    # تخزين مؤقت في قاعدة بيانات أو cache (مثلاً Redis) مع وقت انتهاء
    # هنا مثال بسيط:
    result.secure_token = token
    result.save()
    return f"https://lab.com/result/{token}"

def generate_otp(patient):
    code = str(random.randint(100000, 999999))
    otp = OTP.objects.create(
        patient=patient,
        code=code,
        expires_at=timezone.now() + timedelta(minutes=10)
    )
    return code

def send_sms(phone, message):
    # للتجربة فقط (ممكن لاحقًا نربطه ب Twilio أو WhatsApp API)
    print(f"SMS to {phone}: {message}")
