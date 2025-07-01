[![Go](https://img.shields.io/badge/Go-1.21-blue?logo=go)](https://golang.org/)

# NeuroHabits - An Intelligent Habit Tracking & Motivation System

**NeuroHabits**, a product currently in development as of 2025/2026, will be an AI-driven habit-tracking application designed to help users build and sustain positive routines. By integrating neuroscience principles and artificial intelligence, NeuroHabits will provide a variety of personalized motivational insights and progress tracking through the safe and secure monitoring of a user's day-to-day activities.

## Key Features
- **AI-Powered Motivation:** Tailored prompts and feedback to keep you inspired.
- **Effortless Habit Management:** Simple understandable tools to track your progress and achievements.
- **Seamless Integration:** A robust Python (Flask/FastAPI) backend and a modern React frontend.
- **Scalable & Secure:** Deployed on AWS for reliable and secure user experiences.

Let's start building habits that stick with NeuroHabits! 🚀

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 16+
- AWS Account (for production deployment)
- Contact repository owner (Tameem Hossain) for development credentials

### Local Development

1. Clone the repository
2. Contact the repository owner for development credentials and environment configuration
3. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ../frontend
   npm install
   ```
4. Run the development servers:
   ```bash
   # Backend
   cd backend
   flask run
   
   # Frontend
   cd frontend
   npm start
   ```

## Project Structure

- `backend/`: Flask application
- `frontend/`: React application
- `tests/`: Test suite
- `.github/workflows/`: CI/CD workflows

## Testing

Run the test suite:
```bash
cd backend
python -m pytest
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Contact the repository owner for necessary credentials
4. Make your changes
5. Submit a pull request

## Deployment

The application is automatically deployed when changes are pushed to the main branch. Deployment credentials are managed privately by the repository owner.

## Contact

For development credentials, deployment access, or any other inquiries, please contact:
- **Tameem Hossain** (Repository Owner)
- GitHub: [Your GitHub Profile]
- Email: [Your Professional Email]

## RL/Statistical Prediction API Endpoints

### Generate Predictions for All Habits
POST `/api/habit/predictions/generate`
```json
{
  "user_id": "testuser"
}
```
Returns: `{ "message": "Predictions generated and stored", "results": [...] }`

### Get Predictions for a Habit
GET `/api/habit/predictions/get?user_id=testuser&habit_id=habit1`
Returns: `{ "predictions": [...] }`

### Get Feedback for a Habit Based on Predictions
GET `/api/habit/predictions/feedback?user_id=testuser&habit_id=habit1`
Returns: `{ "feedbacks": [...] }`

### Train RL Model for a Habit
POST `/api/habit/predictions/rl_train`
```json
{
  "user_id": "testuser",
  "habit_id": "habit1"
}
```
Returns: `{ "message": "RL model trained for habit", "habit_id": "habit1" }`

## Concurrency & Go ML Detection Service

- The backend uses Python's ThreadPoolExecutor to run ML detection for multiple habits in parallel, greatly speeding up prediction generation.
- A Go microservice (`go-ml-detect`) can be integrated for even faster, concurrent ML detection. The Python backend can call this service for batch predictions.
- Configure the Go service endpoint via the `GO_ML_SERVICE_URL` environment variable (default: http://localhost:9000).

### Go ML Service API (example)
- POST `/detect`
  - Request: `{ "habits": [ { "habit_id": "...", "logs": [...] }, ... ] }`
  - Response: `{ "predictions": [ ... ] }`

- The Python backend will automatically use concurrency for prediction generation, and can be extended to call the Go service for even greater speed.

# Golang Integration

This repository features a high-performance Go microservice (`go-ml-detect`) for concurrent ML habit detection. The Go service exposes REST endpoints for batch prediction, health checks, and service stats, and is integrated with the Python backend for fast, concurrent ML detection.

**Go Endpoints:**
- `POST /detect` — Batch habit prediction (concurrent)
- `GET /health` — Health check
- `GET /version` — Service version
- `GET /stats` — Service stats (uptime, goroutines, Go version)

The Python backend can call the Go service for ML detection, and the Go service is included in the Docker Compose setup for easy deployment.
