from django.contrib import admin

from .models import Attendance, Student
from .utils import load_known_faces, reset_autoincrement


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

    def _post_student_delete_housekeeping(self):
        """
        Keep DB integrity and UI behavior predictable after deletes.

        We never rewrite existing PK IDs; only reset SQLite sequence when the
        table is fully empty so the next fresh insert can start from 1.
        """
        if Student.objects.count() == 0:
            reset_autoincrement()
        load_known_faces(force_reload=True)

    def delete_queryset(self, request, queryset):
        super().delete_queryset(request, queryset)
        self._post_student_delete_housekeeping()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        self._post_student_delete_housekeeping()


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("id", "student", "date", "time")
    list_filter = ("date", "student")
    search_fields = ("student__name",)
