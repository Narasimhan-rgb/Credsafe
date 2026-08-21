# CredSafe – TrustVerify

**Verify the Loan. Protect the Trust.**

CredSafe / LoanGuard is a hackathon prototype for AI-assisted loan-utilization verification with risk-gated security protection.

## Core Features

- Mobile-number + OTP beneficiary authentication
- Loan and beneficiary workflow
- Geo/time-aware evidence handling
- AI/FastAPI risk analysis
- Device, IP, login-velocity and behavioural security signals
- Account-takeover scenario detection
- Security event correlation and prioritized response
- PostgreSQL-backed audit and application data

## Stack

- Java 21 + Spring Boot
- Python + FastAPI
- React/Vite frontend
- PostgreSQL
- REST APIs

## Project Structure

- `ai-service/` – Python/FastAPI AI and security-risk services
- `backend/` – Java/Spring Boot backend
- `frontend/` – LoanGuard web frontend

## Run Locally

### AI service

```bash
cd ai-service
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### Backend

Copy `backend/src/main/resources/application.properties.example` to `application.properties`, set your local PostgreSQL credentials, then run the Spring Boot application.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend is served by Vite on port `5173` and proxies API requests to the Spring Boot backend on port `8080`.

## Security Note

This repository intentionally excludes local virtual environments, dependency folders, build artifacts, uploaded evidence, and local secrets/credentials.

## Prototype Status

This is a hackathon/research prototype. Production deployment should use HTTPS, proper secret management, hardened authentication, production-grade observability and external threat-intelligence sources.
