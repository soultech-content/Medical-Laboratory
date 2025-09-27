from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('book/', views.book_appointment_view, name='book-appointment'),
    path('confirm/<int:appointment_id>/', views.confirm_otp_view, name='confirm-otp'),
]

