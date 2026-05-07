# Face Recognition Attendance System

This is a Django web app for student attendance using face recognition. It lets you register students with face images, scan a browser webcam frame, compare it with registered faces, and mark attendance once per student per day.

## Deployment on Vercel

The app now uses AWS Rekognition for face recognition, which avoids native library issues on Vercel.

### Setup AWS Credentials

1. Create an AWS account and set up Rekognition and S3 (if needed).
2. In Vercel dashboard, add environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_REGION` (e.g., `us-east-1`)

### Migrate Existing Data

If you have existing students, run the management command locally before deploying:

```bash
python manage.py index_faces
```

This will index existing student faces in AWS Rekognition.

## What Was Fixed For Portability

The project was previously tied to one local computer because some scripts used hard-coded paths like:

```bat
c:/Users/pande/OneDrive/Desktop/face recognization/...
```

That has been fixed. The project now includes:

- `start_project.bat` - creates a virtual environment, installs dependencies, migrates the database, and starts the server.
- `install_dependencies.bat` - installs all packages from `requirements.txt`.
- Updated `run_createsuperuser.bat` - no hard-coded computer path.
- Updated `install_cv2.bat` - no hard-coded computer path.
- Environment-based Django settings for `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and database path.
- `Dockerfile` and `docker-compose.yml` for a more consistent setup across different computers.
- `make_project_zip.bat` to create a clean ZIP without virtual environments and cache files.

## Can This Run On Another Computer?

Yes, but not by only opening the folder. The other computer still needs either:

1. Python installed, then run `start_project.bat`.
2. Docker installed, then run `docker compose up --build`.

The hardest dependency is `face_recognition`, because it uses `dlib`, which may require build tools on Windows. Docker is usually the smoother option because it installs the Linux system dependencies inside the container.

## Project Structure

```text
face recognization/
+-- attendance/
|   +-- models.py
|   +-- urls.py
|   +-- utils.py
|   +-- views.py
+-- media/
|   +-- students/
+-- project/
|   +-- manage.py
|   +-- project/
|       +-- settings.py
|       +-- urls.py
|       +-- asgi.py
|       +-- wsgi.py
+-- static/
|   +-- css/
+-- templates/
+-- Dockerfile
+-- docker-compose.yml
+-- requirements.txt
+-- start_project.bat
+-- make_project_zip.bat
+-- README.md
```

## Option 1: Run On Windows With One Script

Use this option if the computer has Python installed.

1. Extract the ZIP.
2. Open the extracted `face recognization` folder.
3. Double-click:

   ```text
   start_project.bat
   ```

4. Wait for dependencies and migrations to finish.
5. Open:

   ```text
   http://127.0.0.1:8000/
   ```

The script will:

- Create `.project_venv` if missing.
- Activate the virtual environment.
- Upgrade pip.
- Install dependencies.
- Run Django migrations.
- Start the Django development server.

## Option 2: Run With Docker

Use this option if the computer has Docker Desktop installed.

1. Extract the ZIP.
2. Open a terminal in the extracted project folder.
3. Run:

   ```powershell
   docker compose up --build
   ```

4. Open:

   ```text
   http://127.0.0.1:8000/
   ```

To stop Docker, press `Ctrl+C` in the terminal.

Docker stores its database and uploaded media in Docker volumes named:

```text
attendance_db
attendance_media
```

## Deploying On Vercel

The project now includes Vercel-compatible entrypoints:

```text
api/index.py
app.py
index.py
main.py
manage.py
pyproject.toml
vercel.json
```

If Vercel says `No python entrypoint found`, make sure the deployed ZIP or GitHub repository includes these files at the folder root that Vercel is importing.

The preferred Vercel flow is:

1. Deploy the project folder that contains `api/index.py`.
2. Keep the Framework Preset as **Other** if Vercel asks.
3. Add a production environment variable:

   ```text
   DJANGO_SECRET_KEY
   ```

4. Redeploy.

Important: Vercel is serverless. SQLite files and uploaded media are not a good permanent storage solution there. For a real hosted version, use a hosted database and external media storage. Also, `face_recognition` depends on native `dlib` builds, so Vercel may still fail later during dependency installation even after the entrypoint issue is fixed.

## Manual Setup

If you do not want to use the script or Docker, run these commands manually.

Open PowerShell or terminal in the project folder:

```powershell
cd "path\to\face recognization"
```

Create virtual environment:

```powershell
python -m venv .venv
```

Activate virtual environment:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run migrations:

```powershell
cd project
python manage.py migrate
```

Create admin user:

```powershell
python manage.py createsuperuser
```

Start server:

```powershell
python manage.py runserver 127.0.0.1:8000
```

Open:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

## How To Use The App

1. Open the home page.
2. Go to **Register Student**.
3. Enter the student name.
4. Upload a clear face image or capture one using the webcam.
5. Save the student.
6. Go to **Start Attendance**.
7. Allow camera permission in the browser.
8. Keep the face visible in the webcam.
9. The system recognizes the face and marks attendance.
10. Go to **View Report** to see records or download CSV.

## Creating A ZIP To Send

Run:

```text
make_project_zip.bat
```

This creates:

```text
face-recognition-attendance.zip
```

The ZIP helper skips heavy/local folders such as `.venv`, `.venv310`, `.project_venv`, `__pycache__`, and `staticfiles`.

## Sharing Existing Student Data

If you want the other person to receive your existing students and attendance records, include both:

```text
db.sqlite3
media/
```

These two must stay together. The database stores image paths, and the actual photos are inside `media/students/`.

If you do not share them, the other person can still run the app but must register students again.

## If `face_recognition` Fails On Windows

Try these fixes:

1. Use Python 3.10 or 3.11.
2. Install Visual Studio Build Tools with C++ build support.
3. Install CMake:

   ```powershell
   pip install cmake
   ```

4. Run:

   ```powershell
   pip install dlib
   pip install face_recognition
   ```

5. Run `start_project.bat` again.

If this still fails, use Docker instead.

## Why It Is Still Not A Public Hosted App

This project is now portable for another computer, but it is still configured as a local/development app. For LAN or public hosting, you still need to:

- Set a real `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=False`.
- Set `DJANGO_ALLOWED_HOSTS` to the server IP/domain.
- Configure static and media file serving.
- Use HTTPS if remote browsers need camera access.
- Use a production server instead of Django's development server.

## Environment Variables

Optional settings:

```text
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_CSRF_TRUSTED_ORIGINS
DJANGO_DATABASE_NAME
```

Example:

```powershell
$env:DJANGO_ALLOWED_HOSTS="127.0.0.1,localhost,192.168.1.10"
python manage.py runserver 0.0.0.0:8000
```

## Notes

- Use clear student images with only one visible face.
- Poor lighting can reduce recognition accuracy.
- Browser webcam access needs permission.
- Remote camera access usually needs HTTPS.
- If no students are registered, attendance recognition will show an error.
