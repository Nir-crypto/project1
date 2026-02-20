# Reward-Based Erudition Platform

Full-stack adaptive assessment platform with ML-based skill-level prediction and course recommendation.

## Tech Stack
- Frontend: React (Vite), React Router, Axios, Tailwind CSS, react-hot-toast
- Backend: Django, Django REST Framework, SimpleJWT
- Database: MySQL
- ML: scikit-learn (Decision Tree, Random Forest, NearestNeighbors)

## Project Structure
```text
/backend
/frontend
/ml
/dataset
README.md
.env.example
```

## 1) Prerequisites (Windows)
- Python 3.11 or 3.12 (recommended for best package wheel compatibility)
- Node.js 18+
- MySQL 8+
- Git (optional)

## 2) MySQL Setup
Open MySQL shell and run:

```sql
CREATE DATABASE reward_erudition CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'reward_user'@'localhost' IDENTIFIED BY 'reward_password';
GRANT ALL PRIVILEGES ON reward_erudition.* TO 'reward_user'@'localhost';
FLUSH PRIVILEGES;
```

## 3) Environment Setup
From project root, copy `.env.example` to `backend/.env` and update values if needed.

## 4) Backend Setup
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run migrations:
```powershell
python manage.py migrate
```

Seed data:
```powershell
python manage.py seed_interests
python manage.py seed_courses
python manage.py seed_questions
python manage.py seed_feedback_questions
```

Generate and train ML models:
```powershell
cd ..
python ml/generate_data.py --samples 400 --seed 42
python ml/train_models.py
cd backend
```

Start backend:
```powershell
python manage.py runserver
```

Backend base URL: `http://127.0.0.1:8000/api`

## 5) Frontend Setup
Open a second terminal:
```powershell
cd frontend
npm install
```

Create `frontend/.env` (optional):
```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

Run frontend:
```powershell
npm run dev
```

Frontend URL: `http://127.0.0.1:5173`

## 6) API Endpoints
Auth:
- `GET /api/interests`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

Dashboard:
- `GET /api/dashboard`
- `GET /api/dashboard/status` (includes `pending_final`)

Courses:
- `GET /api/courses`

Adaptive assessment:
- `POST /api/assessment/start` (`selected_course_id` required)
- `POST /api/assessment/answer`

Result:
- `GET /api/result/:attempt_id`

Final assessment:
- `POST /api/final/start`
- `POST /api/final/submit`
- `POST /api/final/retry`

Feedback:
- `GET /api/feedback/questions`
- `POST /api/feedback/submit`
- `GET /api/feedback/fail-options`
- `POST /api/feedback/fail-submit`

Roadmap:
- `GET /api/roadmap/<course_id>`

## 7) API Smoke Test
After backend is running and DB is seeded:

```powershell
cd backend
python scripts/api_smoke_test.py
```

Optional custom base URL:
```powershell
$env:API_BASE_URL=\"http://127.0.0.1:8000/api\"
python scripts/api_smoke_test.py
```

## 8) Adaptive Scoring Formula
At assessment end:
- `accuracy = correct_count / total_questions`
- `time_factor = clamp(1 - (avg_time_per_question / target_time), 0, 1)`
- `consistency = max_correct_streak / total_questions`
- `overall_points = round(70*accuracy + 20*time_factor + 10*consistency, 2)`

## 9) Common Errors + Fixes
1. `mysqlclient` install fails
- Install Visual C++ Build Tools and MySQL Connector/C.
- Or use prebuilt wheels that match your Python version.

2. `Access denied for user` in Django
- Confirm `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT` in `backend/.env`.
- Verify user grants in MySQL.

3. `No module named rest_framework`
- Activate backend virtual environment and re-run `pip install -r requirements.txt`.

4. Frontend cannot call backend (CORS/network)
- Ensure backend runs on `127.0.0.1:8000`.
- Check `VITE_API_BASE_URL` and `.env`.

5. ML artifact missing
- Run:
  - `python ml/generate_data.py`
  - `python ml/train_models.py`

6. `pip install -r backend/requirements.txt` fails on Python 3.14+
- Use Python 3.11 or 3.12. Some pinned scientific packages may not yet provide wheels for newer Python releases.

## 10) Notes
- Registration requires at least 2 interests.
- Registration now includes `phone_number` and `status` (`Student/Working/Unemployed/Other`).
- Login uses stored DB credentials with JWT.
- Assessment flow: Dashboard -> Select Course -> Adaptive Quiz.
- Dashboard exposes `Final Assessment Pending` and supports resume flow.
- On final fail, user must submit difficulty feedback before retry.
- Feedback submission is allowed only after passing final assessment for a course.
- `overall_points` is the single result metric shown on UI.
