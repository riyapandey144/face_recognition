import csv

import cv2
import pandas as pd
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_GET, require_POST

from .models import Attendance, Student
from .utils import current_date_time, decode_base64_image, load_known_faces, recognize_face_from_frame, index_student_face


def home(request):
    """Render dashboard homepage."""
    return render(request, "home.html")


@require_POST
def _save_student_from_post(request):
    """Create student from upload or captured webcam image."""
    name = request.POST.get("name", "").strip()
    uploaded_image = request.FILES.get("image")
    captured_image = request.POST.get("captured_image", "")

    if not name:
        messages.error(request, "Student name is required.")
        return redirect("register_student")

    if not uploaded_image and not captured_image:
        messages.error(request, "Please upload an image or capture from webcam.")
        return redirect("register_student")

    if captured_image and not uploaded_image:
        from django.core.files.base import ContentFile

        image_array = decode_base64_image(captured_image)
        success, encoded = cv2.imencode(".jpg", image_array)
        if not success:
            messages.error(request, "Failed to process captured image.")
            return redirect("register_student")
        uploaded_image = ContentFile(encoded.tobytes(), name=f"{name.replace(' ', '_')}.jpg")

    student = Student.objects.create(name=name, image=uploaded_image)
    # Index the face in AWS Rekognition
    try:
        index_student_face(student, uploaded_image)
    except Exception as e:
        messages.warning(request, f"Student registered but face indexing failed: {e}")
    load_known_faces(force_reload=True)
    messages.success(request, "Student registered successfully.")
    return redirect("register_student")


def register_student(request):
    """Render registration page and handle student creation."""
    if request.method == "POST":
        return _save_student_from_post(request)
    students = Student.objects.all().order_by("name")
    return render(request, "register.html", {"students": students})


def attendance_page(request):
    """Render attendance page with live recognition."""
    return render(request, "attendance.html")


@require_POST
def recognize_face(request):
    """Recognize face from frame and mark attendance once per day."""
    frame_data = request.POST.get("frame")
    if not frame_data:
        return JsonResponse({"status": "error", "message": "No frame data provided."}, status=400)

    try:
        frame = decode_base64_image(frame_data)
        recognition_result = recognize_face_from_frame(frame)
    except Exception as exc:
        return JsonResponse({"status": "error", "message": f"Processing error: {exc}"}, status=500)

    if recognition_result["status"] != "recognized":
        return JsonResponse(recognition_result)

    student_id = recognition_result["student_id"]
    date_today, time_now = current_date_time()
    try:
        attendance, created = Attendance.objects.get_or_create(
            student_id=student_id,
            date=date_today,
            defaults={"time": time_now},
        )
    except IntegrityError:
        created = False
        attendance = Attendance.objects.get(student_id=student_id, date=date_today)

    recognition_result["attendance_status"] = "Attendance Marked" if created else "Already Marked"
    recognition_result["date"] = str(attendance.date)
    recognition_result["time"] = attendance.time.strftime("%H:%M:%S")
    return JsonResponse(recognition_result)


@require_GET
def report_page(request):
    """Render attendance report with optional date filter."""
    selected_date = request.GET.get("date", "").strip()
    attendances = Attendance.objects.select_related("student").all()
    if selected_date:
        parsed_date = parse_date(selected_date)
        if parsed_date:
            attendances = attendances.filter(date=parsed_date)
    context = {"attendances": attendances, "selected_date": selected_date}
    return render(request, "report.html", context)


@require_GET
def download_report(request):
    """Download attendance report as CSV using pandas."""
    selected_date = request.GET.get("date", "").strip()
    attendances = Attendance.objects.select_related("student").all()
    if selected_date:
        parsed_date = parse_date(selected_date)
        if parsed_date:
            attendances = attendances.filter(date=parsed_date)

    data = [
        {"Student Name": row.student.name, "Date": row.date.strftime("%Y-%m-%d"), "Time": row.time.strftime("%H:%M:%S")}
        for row in attendances
    ]
    dataframe = pd.DataFrame(data if data else [{"Student Name": "", "Date": "", "Time": ""}])

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="attendance_report.csv"'
    dataframe.to_csv(path_or_buf=response, index=False, quoting=csv.QUOTE_MINIMAL)
    return response
