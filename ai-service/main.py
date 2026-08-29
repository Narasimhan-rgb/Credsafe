from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from loan.image_verification import verify_image
from loan.geo_time_verification import verify_geo_time
from loan.purpose_verification import verify_purpose_consistency
from loan.evidence_risk import calculate_evidence_risk
from loan.loan_risk import calculate_loan_risk


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="SecureLoan AI Service",
    description=(
        "AI-powered loan utilization and "
        "security verification engine"
    ),
    version="1.2.0"
)


# =========================================================
# EVIDENCE VERIFICATION REQUEST
# =========================================================

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


# =========================================================
# EVIDENCE VERIFICATION RESPONSE
# =========================================================

class EvidenceVerificationResponse(BaseModel):

    result: str

    confidence: float

    reason: str

    recommendation: str


# =========================================================
# LOAN RISK REQUEST MODELS
# =========================================================

class LoanEvidenceRiskItem(BaseModel):

    evidenceId: int

    result: str

    riskScore: int


class LoanRiskRequest(BaseModel):

    loanId: int

    evidence: list[LoanEvidenceRiskItem]


# =========================================================
# LOAN RISK RESPONSE
# =========================================================

class LoanRiskResponse(BaseModel):

    loanId: int

    riskScore: int

    riskLevel: str

    evidenceCount: int

    validEvidence: int

    suspiciousEvidence: int

    recommendation: str


# =========================================================
# ROOT ENDPOINT
# =========================================================

@app.get("/")
def root():

    return {
        "service": "SecureLoan AI Service",
        "version": "1.2.0",
        "status": "running"
    }


# =========================================================
# HEALTH ENDPOINT
# =========================================================

@app.get("/health")
def health():

    return {
        "status": "UP"
    }


# =========================================================
# EVIDENCE VERIFICATION
# =========================================================

@app.post(
    "/api/verify/evidence",
    response_model=EvidenceVerificationResponse
)
def verify_evidence(
    request: EvidenceVerificationRequest
):

    print("\n========================================")
    print("SECURELOAN AI VERIFICATION STARTED")
    print("========================================")

    print(
        "Evidence ID:",
        request.evidenceId
    )

    print(
        "Evidence Type:",
        request.evidenceType
    )

    print(
        "File Path:",
        request.filePath
    )

    print(
        "Loan Purpose:",
        request.loanPurpose
    )


    # =====================================================
    # EVIDENCE TYPE CHECK
    # =====================================================

    evidence_type = (
        request
        .evidenceType
        .upper()
    )

    if evidence_type != "PHOTO":

        return EvidenceVerificationResponse(

            result="SUSPICIOUS",

            confidence=0.70,

            reason=(
                f"Evidence type "
                f"{evidence_type} "
                f"is not currently supported "
                f"by the AI verification model"
            ),

            recommendation=
                "MANUAL_REVIEW"
        )


    # =====================================================
    # 1. IMAGE QUALITY VERIFICATION
    # =====================================================

    print("\n--- IMAGE VERIFICATION ---")

    image_result = verify_image(

        request.filePath,

        request.loanPurpose
    )

    print(
        "IMAGE RESULT:",
        image_result
    )


    # =====================================================
    # 2. PURPOSE ↔ IMAGE AI VERIFICATION
    # =====================================================

    print("\n--- PURPOSE VERIFICATION ---")

    purpose_result = (
        verify_purpose_consistency(

            request.filePath,

            request.loanPurpose
        )
    )

    print(
        "PURPOSE AI RESULT:",
        purpose_result
    )


    # =====================================================
    # 3. GEO + TIME + METADATA ANALYSIS
    # =====================================================

    print("\n--- GEO / TIME VERIFICATION ---")

    geo_result = verify_geo_time(

        latitude=
            request.latitude,

        longitude=
            request.longitude,

        captured_at=
            request.capturedAt,

        metadata_valid=
            request.metadataValid,

        geo_verified=
            request.geoVerified
    )

    print(
        "GEO/TIME RESULT:",
        geo_result
    )


    # =====================================================
    # 4. COMBINED EVIDENCE RISK ENGINE
    # =====================================================

    print("\n--- COMBINED AI RISK ---")

    final_result = (
        calculate_evidence_risk(

            image_result,

            geo_result,

            purpose_result
        )
    )

    print(
        "FINAL RESULT:",
        final_result
    )

    print("========================================")
    print("SECURELOAN AI VERIFICATION COMPLETED")
    print("========================================\n")


    # =====================================================
    # RETURN RESULT TO SPRING BOOT
    # =====================================================

    return EvidenceVerificationResponse(

        result=
            final_result[
                "result"
            ],

        confidence=
            final_result[
                "confidence"
            ],

        reason=
            final_result[
                "reason"
            ],

        recommendation=
            final_result[
                "recommendation"
            ]
    )


# =========================================================
# LOAN LEVEL RISK VERIFICATION
# =========================================================

@app.post(
    "/api/verify/loan-risk",
    response_model=LoanRiskResponse
)
def verify_loan_risk(
    request: LoanRiskRequest
):

    print("\n========================================")
    print("LOAN LEVEL RISK ANALYSIS")
    print("Loan ID:", request.loanId)
    print("========================================")


    # =====================================================
    # CONVERT PYDANTIC DATA TO DICTIONARY LIST
    # =====================================================

    items = []

    for evidence in request.evidence:

        items.append({

            "evidenceId":
                evidence.evidenceId,

            "result":
                evidence.result,

            "riskScore":
                evidence.riskScore
        })


    # =====================================================
    # CALCULATE LOAN RISK
    # =====================================================

    risk = calculate_loan_risk(
        items
    )


    print(
        "LOAN RISK RESULT:",
        risk
    )


    # =====================================================
    # RETURN LOAN RISK
    # =====================================================

    return LoanRiskResponse(

        loanId=
            request.loanId,

        riskScore=
            risk[
                "riskScore"
            ],

        riskLevel=
            risk[
                "riskLevel"
            ],

        evidenceCount=
            risk[
                "evidenceCount"
            ],

        validEvidence=
            risk[
                "validEvidence"
            ],

        suspiciousEvidence=
            risk[
                "suspiciousEvidence"
            ],

        recommendation=
            risk[
                "recommendation"
            ]
    )