from django.db import models
from django.utils import timezone
from datetime import timedelta

class Patient(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"
    
    def check_otp(self, code):
            otp = OTP.objects.filter(patient=self, code=code).order_by('-id').first()
            if otp and otp.is_valid():
                return True
            return False



class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending_confirmation', 'Pending Confirmation'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
    ]
    LOCATION_CHOICES = [
        ('lab', 'Lab'),
        ('home', 'Home'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=255, blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending_confirmation')
    location = models.CharField(max_length=20, choices=LOCATION_CHOICES, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment({self.patient.name} - {self.status})"

class Result(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='results/')
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.CharField(max_length=255, blank=True, null=True)

class OTP(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=6, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def is_valid(self):
        return self.expires_at and timezone.now() < self.expires_at

    def save(self, *args, **kwargs):
        import random
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP {self.code} for {self.patient.phone if self.patient else 'Unknown'}"
