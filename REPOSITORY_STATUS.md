# Repository status — 22 September 2026

## Role

Loan evidence verification prototype with a FastAPI service, Vite frontend and a partial Java backend export.

## Reproduction

AI: `cd ai-service`, create/activate a virtual environment, `pip install -r requirements.txt`, then `python -m uvicorn main:app --host 127.0.0.1 --port 8000`. Frontend: `cd frontend`, `npm ci`, `npm run dev`.

## Outstanding work

The Java export is incomplete: AuthService, DTOs, entities, repositories, behavior/familiar-fraud services, application entry point, and loan/evidence/officer routes are missing. Restore the original backend source to preserve the intended data model and behavior. There is no Maven wrapper in this repo. The frontend cannot complete the workflow until that backend is restored. Optional CLIP model weights and dependencies are needed for purpose matching; otherwise manual review is required. Empty investigation/response/security Python files are unused scaffolding, not implemented engines.

Build or unit-test success is not evidence of a deployed service or a completed research evaluation. See the pull request for checks executed for this revision.

## Checks executed in this pass

Frontend production build passed. OTP source now uses SecureRandom, suppresses OTP logging and limits failed attempts. Full Java backend cannot compile until missing source is restored; OTP changes have not been verified in the complete application.
