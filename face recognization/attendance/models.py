from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .utils import remove_student_face


class Student(models.Model):
    """Stores registered student details and their reference image."""

    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to="students/")

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Student)
def delete_student_face(sender, instance, **kwargs):
    """Remove student's face from AWS Rekognition when student is deleted."""
    remove_student_face(instance.id)


class Attendance(models.Model):
    """Stores daily attendance entries for students."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField()
    time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "date"], name="unique_student_daily_attendance")
        ]
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.student.name} - {self.date} {self.time}"
