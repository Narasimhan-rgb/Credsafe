# CredSafe – TrustVerify

**Verify the Loan. Protect the Trust.**

CredSafe / LoanGuard is a hackathon prototype for AI-assisted loan-utilization verification with risk-gated security protection. It combines OTP-based beneficiary authentication, real-time security risk correlation, and AI-driven evidence (photo) verification to catch account takeover and loan-fraud attempts while confirming that disbursed funds are used for their stated purpose.

> ⚠️ Hackathon/research prototype — not production-hardened. See **Prototype Status** below.

---

## Core Features

- Mobile-number + OTP beneficiary authentication, with new-account registration
- Loan lifecycle and beneficiary consent workflow (create → consent → activate → verify → approve/reject/hold)
- Evidence upload with geo/time-aware and metadata validation
- AI/FastAPI risk analysis: image quality, purpose-consistency, and combined evidence risk scoring
- Device, IP, login-velocity, and behavioural security signals
- Account-takeover scenario detection
- Security event correlation, incident tracking, and prioritized response
- Officer review console for case decisions
- PostgreSQL-backed audit trail and application data

---

## Stack

- **Backend:** Java 21 + Spring Boot (Web, Data JPA, Security, Validation, Actuator, RestClient)
- **AI Service:** Python + FastAPI, Pydantic, Pillow
- **Frontend:** Vite-served vanilla JavaScript SPA *(single-page `index.html`, no framework)*
- **Database:** PostgreSQL
- **Communication:** REST APIs

---

## Project Structure

- `ai-service/` – Python/FastAPI AI and security-risk services
- `backend/` – Java/Spring Boot backend
- `frontend/` – LoanGuard web frontend (includes `backend-patch/`, a drop-in Spring Boot patch that adds account registration — copy it into the backend's `com.secureloan` package if it isn't merged yet)

---

## Core API Endpoints

**Backend (`:8080/api/...`)**
| Endpoint | Purpose |
|---|---|
| `POST /auth/register` | Create a new beneficiary account |
| `POST /auth/request-otp` / `POST /auth/verify-otp` | OTP login flow |
| `GET /loans/user/{userId}`, `GET /loans/{loanId}` | Loan lookup |
| `POST /loans/consent`, `POST /loans/activate` | Consent & activation |
| `POST /evidence/upload`, `GET /evidence/loan/{loanId}`, `POST /evidence/{id}/verify` | Evidence handling & AI verification trigger |
| `GET /officer/cases`, `GET /officer/cases/{loanId}`, `POST /officer/.../decision` | Officer case review |
| `POST /security/assess` | Real-time security risk assessment |

**AI Service (`:8000/api/...`)**
| Endpoint | Purpose |
|---|---|
| `GET /health` | Health check |
| `POST /verify/evidence` | Image quality + purpose match + geo/time check for one item of evidence |
| `POST /verify/loan-risk` | Aggregate loan-level risk from all evidence |

---

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
Copy `backend/src/main/resources/application.properties.example` to `application.properties`, set your local PostgreSQL credentials, then run the Spring Boot application (`./mvnw spring-boot:run`).

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend is served by Vite on port `5173` and proxies `/api` requests to the Spring Boot backend on port `8080`.

Run all three services together — the frontend depends on the backend, which depends on the AI service.

---

## Security Note

This repository intentionally excludes local virtual environments, dependency folders, build artifacts, uploaded evidence, and local secrets/credentials. Real database credentials must live only in your local, git-ignored `application.properties` — never commit them.

> **Action needed before pushing:** the working copy currently has real credentials hardcoded directly in `application.properties`. Move them into `application.properties.example` (with placeholder values) and add the real file to `.gitignore` before this note is accurate.

The `investigation/` and `response/` modules under `ai-service/` are scaffolded for future automated investigation and response-recommendation logic — they're currently empty placeholders, not yet wired in.

---

## Prototype Status

This is a hackathon/research prototype. Production deployment should use HTTPS, proper secret management, hardened authentication, production-grade observability, and external threat-intelligence sources.

---

## Authors

| Role | Name | Contribution |
|---|---|---|
| **Backend Developer** | *Narasimhan D* | Spring Boot backend — auth, loan lifecycle, evidence handling, security risk correlation, officer workflow, DB schema |
| **Frontend Developer** | *Raghunanthan R* | LoanGuard SPA — login/registration, OTP flow, loan dashboard, evidence upload UI, security scenario simulator |
| **AI/ML Developer** | *Vijay Nishal Magesh Kumar* | FastAPI verification service — image quality, purpose-consistency, geo/time validation, combined risk engines |

