from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from loan.image_verification import verify_image
from loan.geo_time_verification import verify_geo_time
from loan.purpose_verification import verify_purpose_consistency
from loan.evidence_risk import calculate_evidence_risk
from loan.loan_risk import calculate_loan_risk

app = FastAPI(
    title="SecureLoan AI Service",
    description="AI-powered loan utilization and security verification engine",
    version="1.2.0"
)

class EvidenceVerificationRequest(BaseModel):
    evidenceId: int
    evidenceType: str
    filePath: str
    fileHash: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    capturedAt: Optional[str] = None
    loanPurpose: Optional[str] = None
    metadataValid: bool
    geoVerified: bool

class EvidenceVerificationResponse(BaseModel):
    result: str
    confidence: float
    reason: str
    recommendation: str

class LoanEvidenceRiskItem(BaseModel):
    evidenceId: int
    result: str
    riskScore: int

class LoanRiskRequest(BaseModel):
    loanId: int
    evidence: list[LoanEvidenceRiskItem]

class LoanRiskResponse(BaseModel):
    loanId: int
    riskScore: int
    riskLevel: str
    evidenceCount: int
    validEvidence: int
    suspiciousEvidence: int
    recommendation: str

class SecurityAssessmentRequest(BaseModel):
    userId: int
    mobileNumber: str
    ipAddress: str
    deviceFingerprint: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    eventType: str = "LOGIN"
    newDevice: bool = False
    abnormalBehaviour: bool = False
    recentLoginAttempts: int = 1
    otpVerified: bool = False
    browser: Optional[str] = None
    userAgent: Optional[str] = None

@app.get("/")
def root():
    return {"service": "SecureLoan AI Service", "version": "1.2.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "UP"}

@app.post("/api/security/assess")
def assess_security(request: SecurityAssessmentRequest):
    risk = 0
    events = []

    if request.otpVerified:
        events.append({"name": "Identity / OTP", "detail": "OTP successfully verified", "score": 0})
    else:
        risk += 50
        events.append({"name": "Identity / OTP", "detail": "OTP verification failed", "score": 50})

    if request.newDevice:
        risk += 22
        events.append({"name": "Device behaviour", "detail": "New or untrusted device detected", "score": 22})
    else:
        risk += 2
        events.append({"name": "Device behaviour", "detail": "Known device continuity", "score": 2})

    suspicious_ip = request.ipAddress == "198.51.100.66"
    if suspicious_ip:
        risk += 48
        events.append({"name": "CTI / IP reputation", "detail": request.ipAddress + " matched a threat-intelligence IOC", "score": 48})
    else:
        events.append({"name": "CTI / IP reputation", "detail": "No relevant CTI match for " + request.ipAddress, "score": 0})

    if request.recentLoginAttempts >= 4:
        risk += 30
        events.append({"name": "Login velocity", "detail": str(request.recentLoginAttempts) + " login events observed within the window", "score": 30})
    else:
        risk += 2
        events.append({"name": "Login velocity", "detail": str(request.recentLoginAttempts) + " recent login event(s)", "score": 2})

    if request.abnormalBehaviour:
        risk += 16
        events.append({"name": "Behavioural analytics", "detail": "Access pattern deviates from baseline", "score": 16})
    else:
        risk += 2
        events.append({"name": "Behavioural analytics", "detail": "Access pattern within baseline", "score": 2})

    risk = min(100, risk)

    if risk >= 80:
        severity, priority, action = "CRITICAL", "P1", "BLOCK_LOGIN_AND_OPEN_INCIDENT"
        recommendations = ["Deny or revoke session", "Create prioritized security incident", "Preserve correlated event evidence", "Require identity re-validation", "Recommend analyst review"]
    elif risk >= 60:
        severity, priority, action = "HIGH", "P2", "BLOCK_SESSION_AND_INVESTIGATE"
        recommendations = ["Deny or revoke session", "Create prioritized security incident", "Preserve correlated event evidence", "Require identity re-validation"]
    elif risk >= 35:
        severity, priority, action = "MEDIUM", "P3", "REQUIRE_STEP_UP_MFA"
        recommendations = ["Do not trust OTP alone", "Require step-up identity verification", "Increase session monitoring", "Create review event"]
    else:
        severity, priority, action = "LOW", "P4", "ALLOW_AND_MONITOR"
        recommendations = ["Allow login", "Continue behavioural monitoring"]

    return {
        "riskScore": risk,
        "severity": severity,
        "priority": priority,
        "action": action,
        "events": events,
        "recommendations": recommendations,
        "incidentId": "INC-" + str(request.userId),
        "correlated": len(events),
        "ctiRelevant": suspicious_ip,
        "attempts": request.recentLoginAttempts,
        "otpVerified": request.otpVerified
    }

@app.post("/api/verify/evidence", response_model=EvidenceVerificationResponse)
def verify_evidence(request: EvidenceVerificationRequest):
    evidence_type = request.evidenceType.upper()
    if evidence_type != "PHOTO":
        return EvidenceVerificationResponse(
            result="SUSPICIOUS",
            confidence=0.70,
            reason=f"Evidence type {evidence_type} is not currently supported by the AI verification model",
            recommendation="MANUAL_REVIEW"
        )

    image_result = verify_image(request.filePath, request.loanPurpose)
    purpose_result = verify_purpose_consistency(request.filePath, request.loanPurpose)
    geo_result = verify_geo_time(
        latitude=request.latitude,
        longitude=request.longitude,
        captured_at=request.capturedAt,
        metadata_valid=request.metadataValid,
        geo_verified=request.geoVerified
    )
    final_result = calculate_evidence_risk(image_result, geo_result, purpose_result)
    return EvidenceVerificationResponse(
        result=final_result["result"],
        confidence=final_result["confidence"],
        reason=final_result["reason"],
        recommendation=final_result["recommendation"]
    )

@app.post("/api/verify/loan-risk", response_model=LoanRiskResponse)
def verify_loan_risk(request: LoanRiskRequest):
    items = [{"evidenceId": e.evidenceId, "result": e.result, "riskScore": e.riskScore} for e in request.evidence]
    risk = calculate_loan_risk(items)
    return LoanRiskResponse(
        loanId=request.loanId,
        riskScore=risk["riskScore"],
        riskLevel=risk["riskLevel"],
        evidenceCount=risk["evidenceCount"],
        validEvidence=risk["validEvidence"],
        suspiciousEvidence=risk["suspiciousEvidence"],
        recommendation=risk["recommendation"]
    )
