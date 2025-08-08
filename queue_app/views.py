from django.shortcuts import render, redirect
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from .models import Patient, Doctor, Appointment


def index(request):
    """Render the home page with real-time queue data."""

    appointments = Appointment.objects.select_related('patient', 'doctor').annotate(
        priority=Case(
            When(status='Emergency', then=Value(1)),
            When(status='Pending', then=Value(2)),
            When(status='Completed', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('priority', 'appointment_time')

    active_appointments = appointments.filter(status__in=['Emergency', 'Pending'])

    total_patients = active_appointments.count()
    currently_attending = active_appointments.first() if total_patients > 0 else None
    next_in_queue = active_appointments[1] if total_patients > 1 else None

    estimated_waiting_time = None
    if next_in_queue:
        patients_ahead = active_appointments.filter(appointment_time__lt=next_in_queue.appointment_time).count()
        estimated_waiting_time = patients_ahead * 10  # 10 minutes per patient

    context = {
        'total_patients': total_patients,
        'currently_attending': currently_attending.patient.name if currently_attending else 'None',
        'next_in_queue': next_in_queue.patient.name if next_in_queue else 'None',
        'estimated_waiting_time': f"{estimated_waiting_time} minutes" if estimated_waiting_time else 'N/A',
    }
    return render(request, 'index.html', context)


def book_appointment(request):
    """Handles appointment booking."""

    if request.method == 'POST':
        patient_name = request.POST.get('name')
        age = request.POST.get('age')
        symptoms = request.POST.get('symptoms')
        appointment_time = request.POST.get('appointment_time')

        # Validate required fields (basic validation)
        if not all([patient_name, age, symptoms, appointment_time]):
            return render(request, 'book_appointment.html', {
                'error': 'Please fill all the fields before submitting.'
            })

        # Create a new Patient record
        patient = Patient.objects.create(name=patient_name, age=age, symptoms=symptoms)

        # Assign the first available doctor
        doctor = Doctor.objects.filter(available=True).first()

        if doctor:
            # Create appointment with Pending status
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_time=appointment_time,
                status='Pending'
            )
            # Mark the doctor as unavailable
            doctor.available = False
            doctor.save()

            # Prepare appointment data for the template
            appointment_info = {
                'patient_name': patient.name,
                'age': patient.age,
                'symptoms': patient.symptoms,
                'appointment_time': appointment.appointment_time,
                'doctor_name': doctor.name,
                'doctor_specialization': doctor.specialization,
            }

            return render(request, 'book_appointment.html', {'appointment': appointment_info})
        else:
            # No doctor available
            return render(request, 'book_appointment.html', {
                'error': 'Sorry, no doctors are available at the moment. Please try again later.'
            })

    return render(request, 'book_appointment.html')


def queue_status(request):
    """Displays the current queue status."""

    appointments = Appointment.objects.select_related('patient', 'doctor').annotate(
        priority=Case(
            When(status='Emergency', then=Value(1)),
            When(status='Pending', then=Value(2)),
            When(status='Completed', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('priority', 'appointment_time')

    active_appointments = appointments.filter(status__in=['Emergency', 'Pending'])

    total_patients = active_appointments.count()
    currently_attending = active_appointments.first() if total_patients > 0 else None
    next_in_queue = active_appointments[1] if total_patients > 1 else None

    estimated_waiting_time = None
    if next_in_queue:
        patients_ahead = active_appointments.filter(appointment_time__lt=next_in_queue.appointment_time).count()
        estimated_waiting_time = patients_ahead * 10  # 10 minutes per patient

    context = {
        'appointments': appointments,
        'total_patients': total_patients,
        'currently_attending': currently_attending,
        'next_in_queue': next_in_queue,
        'estimated_waiting_time': estimated_waiting_time,
    }
    return render(request, 'queue_status.html', context)


def emergency_treatment(request):
    """Handles emergency appointment booking."""

    if request.method == 'POST':
        patient_name = request.POST.get('name')
        age = request.POST.get('age')
        symptoms = request.POST.get('symptoms')

        # Basic validation
        if not all([patient_name, age, symptoms]):
            return render(request, 'emergency_treatment.html', {
                'error': 'Please fill all the fields before submitting.'
            })

        appointment_time = timezone.now()  # Immediate appointment time

        # Create new patient record
        patient = Patient.objects.create(name=patient_name, age=age, symptoms=symptoms)

        # Assign first available doctor
        doctor = Doctor.objects.filter(available=True).first()

        if doctor:
            # Create emergency appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                appointment_time=appointment_time,
                status='Emergency'
            )
            # Mark doctor unavailable
            doctor.available = False
            doctor.save()

            return render(request, 'emergency_treatment.html', {'success': True, 'appointment': appointment})
        else:
            # No doctors available
            return render(request, 'emergency_treatment.html', {
                'error': 'No doctors available currently. Please wait.'
            })

    return render(request, 'emergency_treatment.html')
