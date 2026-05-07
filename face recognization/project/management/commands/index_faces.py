from django.core.management.base import BaseCommand
from attendance.models import Student
from attendance.utils import index_student_face, _ensure_collection

class Command(BaseCommand):
    help = 'Index existing student faces in AWS Rekognition'

    def handle(self, *args, **options):
        _ensure_collection()
        students = Student.objects.all()
        for student in students:
            if student.image:
                try:
                    index_student_face(student, student.image)
                    self.stdout.write(f'Indexed face for {student.name}')
                except Exception as e:
                    self.stderr.write(f'Failed to index {student.name}: {e}')
        self.stdout.write('Finished indexing faces')