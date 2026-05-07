from django.urls import path

from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_student, name="register_student"),
    path("attendance/", views.attendance_page, name="attendance_page"),
    path("api/recognize/", views.recognize_face, name="recognize_face"),
    path("report/", views.report_page, name="report_page"),
    path("report/download/", views.download_report, name="download_report"),
]
