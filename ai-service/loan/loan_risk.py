from typing import List


def calculate_loan_risk(
    evidence_items: List[dict]
) -> dict:

    if not evidence_items:

        return {
            "riskScore": 80,
            "riskLevel": "HIGH",
            "recommendation":
                "REQUEST_EVIDENCE",
            "reason":
                "No utilization evidence available"
        }

    total_risk = 0

    suspicious_count = 0

    valid_count = 0

    for evidence in evidence_items:

        risk = evidence.get(
            "riskScore",
            50
        )

        total_risk += risk

        result = evidence.get(
            "result",
            "UNKNOWN"
        )

        if result == "SUSPICIOUS":
            suspicious_count += 1

        if result == "VALID":
            valid_count += 1

    average_risk = int(
        total_risk
        /
        len(evidence_items)
    )

    # suspicious evidence adds penalty
    average_risk += (
        suspicious_count * 5
    )

    average_risk = min(
        average_risk,
        100
    )

    if average_risk >= 80:

        level = "CRITICAL"

        recommendation = (
            "BLOCK_AND_INVESTIGATE"
        )

    elif average_risk >= 60:

        level = "HIGH"

        recommendation = (
            "REQUEST_MORE_EVIDENCE"
        )

    elif average_risk >= 35:

        level = "MEDIUM"

        recommendation = (
            "OFFICER_REVIEW"
        )

    else:

        level = "LOW"

        recommendation = (
            "PROCEED_TO_OFFICER_APPROVAL"
        )

    return {

        "riskScore": average_risk,

        "riskLevel": level,

        "evidenceCount":
            len(evidence_items),

        "validEvidence":
            valid_count,

        "suspiciousEvidence":
            suspicious_count,

        "recommendation":
            recommendation
    }