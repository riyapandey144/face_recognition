import base64
import io
import os
from typing import Any

import boto3
import cv2
import numpy as np
from PIL import Image
from django.db import connection
from django.utils import timezone

# AWS Rekognition setup
REKOGNITION_AVAILABLE = False
COLLECTION_ID = os.getenv("AWS_REKOGNITION_COLLECTION_ID", "face-recognition-collection")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

rekognition = None
if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
    try:
        rekognition = boto3.client("rekognition", region_name=AWS_REGION)
        REKOGNITION_AVAILABLE = True
    except Exception:
        import warnings

        warnings.warn("AWS Rekognition is not available. Face recognition features are disabled.")

def _ensure_collection():
    """Ensure the Rekognition collection exists."""
    if not REKOGNITION_AVAILABLE:
        return
    try:
        assert rekognition is not None
        rekognition.create_collection(CollectionId=COLLECTION_ID)
    except rekognition.exceptions.ResourceAlreadyExistsException:
        pass

def remove_student_face(student_id):
    """Remove student's face from AWS Rekognition collection."""
    if not REKOGNITION_AVAILABLE:
        return
    try:
        assert rekognition is not None
        # First, find the face ID
        response = rekognition.list_faces(CollectionId=COLLECTION_ID)
        for face in response['Faces']:
            if face['ExternalImageId'] == str(student_id):
                rekognition.delete_faces(CollectionId=COLLECTION_ID, FaceIds=[face['FaceId']])
                break
    except Exception:
        pass  # Ignore errors if face not found or service unavailable


def decode_base64_image(base64_string: str) -> np.ndarray:
    """Convert base64 image (data URL) into OpenCV BGR image."""
    if "," in base64_string:
        base64_string = base64_string.split(",", 1)[1]
    image_bytes = base64.b64decode(base64_string)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    rgb_array = np.array(image)
    bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
    return bgr_array


def recognize_face_from_frame(frame_bgr: np.ndarray) -> dict[str, Any]:
    """Recognize first detected face from frame using AWS Rekognition."""
    if not REKOGNITION_AVAILABLE:
        return {"status": "error", "message": "AWS Rekognition not available."}
    
    # Convert frame to JPEG bytes
    success, encoded = cv2.imencode('.jpg', frame_bgr)
    if not success:
        return {"status": "error", "message": "Failed to encode frame."}
    image_bytes = encoded.tobytes()
    
    try:
        assert rekognition is not None
        response = rekognition.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={'Bytes': image_bytes},
            FaceMatchThreshold=80.0,
            MaxFaces=1
        )
        
        if not response['FaceMatches']:
            return {"status": "unknown", "message": "Unknown face."}
        
        match = response['FaceMatches'][0]
        student_id = int(match['Face']['ExternalImageId'])
        confidence = match['Similarity']
        
        # Get student name
        from .models import Student

        try:
            student = Student.objects.get(id=student_id)
            name = student.name
        except Student.DoesNotExist:
            return {"status": "error", "message": "Matched face not found in database."}
        
        return {
            "status": "recognized",
            "student_id": student_id,
            "name": name,
            "confidence": confidence,
        }
    except rekognition.exceptions.InvalidParameterException as e:
        if 'no faces' in str(e).lower():
            return {"status": "no_face", "message": "No face detected."}
        return {"status": "error", "message": f"Recognition error: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Recognition error: {str(e)}"}

def current_date_time() -> tuple[Any, Any]:
    """Return current local date and time."""
    now = timezone.localtime()
    return now.date(), now.time().replace(microsecond=0)


def reset_autoincrement():
    """
    Reset SQLite auto-increment sequence for Student IDs when table is empty.

    We intentionally never modify existing primary keys because those IDs can be
    referenced by foreign keys and changing them can break data integrity.
    """
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='attendance_student';")


def index_student_face(student, uploaded_image) -> None:
    """Index a student's uploaded image in AWS Rekognition when credentials exist."""
    if not REKOGNITION_AVAILABLE:
        return

    _ensure_collection()
    uploaded_image.seek(0)
    image_bytes = uploaded_image.read()
    try:
        assert rekognition is not None
        rekognition.index_faces(
            CollectionId=COLLECTION_ID,
            Image={"Bytes": image_bytes},
            ExternalImageId=str(student.id),
            DetectionAttributes=[],
        )
    finally:
        uploaded_image.seek(0)
