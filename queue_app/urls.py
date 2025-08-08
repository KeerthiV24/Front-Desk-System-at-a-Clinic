from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('queue-status/', views.queue_status, name='queue_status'),
    path('emergency-treatment/', views.emergency_treatment, name='emergency_treatment'),  # Emergency treatment URL
]
