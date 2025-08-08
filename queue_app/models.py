from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    symptoms = models.TextField()
    registered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Age: {self.age})"

class Doctor(models.Model):
    name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Emergency', 'Emergency'),
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Appointment for {self.patient.name} with {self.doctor.name} at {self.appointment_time} [{self.status}]"
