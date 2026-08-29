# loan/evidence_risk.py


def calculate_evidence_risk(

    image_result: dict,

    geo_result: dict,

    purpose_result: dict

) -> dict:

    # =====================================================
    # IMAGE QUALITY RISK
    # =====================================================

    image_status = image_result.get(
        "result",
        "SUSPICIOUS"
    )

    image_confidence = float(
        image_result.get(
            "confidence",
            0.0
        )
    )

    if image_status == "VALID":

        image_risk = int(

            (1.0 - image_confidence)

            * 100
        )

    elif image_status == "SUSPICIOUS":

        image_risk = max(

            60,

            int(
                image_confidence
                * 100
            )
        )

    elif image_status == "REJECTED":

        image_risk = 100

    else:

        image_risk = 50


    # =====================================================
    # GEO/TIME RISK
    # =====================================================

    geo_risk = int(

        geo_result.get(
            "risk_score",
            50
        )
    )


    # =====================================================
    # PURPOSE CONSISTENCY RISK
    # =====================================================

    purpose_status = (
        purpose_result.get(
            "result",
            "MANUAL_REVIEW"
        )
    )

    purpose_confidence = float(

        purpose_result.get(
            "confidence",
            0.0
        )
    )

    if purpose_status == "MATCH":

        purpose_risk = int(

            (
                1.0
                -
                purpose_confidence
            )

            * 45
        )

    elif purpose_status == "PARTIAL_MATCH":

        purpose_risk = 50

    elif purpose_status == "MISMATCH":

        purpose_risk = max(

            80,

            int(
                (
                    1.0
                    -
                    purpose_confidence
                )
                * 100
            )
        )

    else:

        purpose_risk = 55


    # =====================================================
    # COMBINED RISK
    #
    # Purpose relationship receives the highest weight.
    # =====================================================

    combined_risk = int(

        image_risk
        * 0.30

        +

        purpose_risk
        * 0.45

        +

        geo_risk
        * 0.25
    )

    combined_risk = min(
        combined_risk,
        100
    )


    # =====================================================
    # FINAL CLASSIFICATION
    # =====================================================

    if combined_risk >= 70:

        final_result = (
            "SUSPICIOUS"
        )

        recommendation = (
            "REQUEST_NEW_EVIDENCE"
        )

    elif combined_risk >= 35:

        final_result = (
            "SUSPICIOUS"
        )

        recommendation = (
            "MANUAL_REVIEW"
        )

    else:

        final_result = (
            "VALID"
        )

        recommendation = (
            "OFFICER_REVIEW"
        )


    # =====================================================
    # OUTPUT CONFIDENCE
    # =====================================================

    decision_distance = abs(

        combined_risk
        -
        50
    )

    confidence = round(

        min(

            0.99,

            0.55

            +

            decision_distance
            / 100
        ),

        2
    )


    # =====================================================
    # EXPLANATION
    # =====================================================

    reason = (

        "Image quality: "
        +
        image_result.get(
            "reason",
            "Unknown"
        )

        +

        " | Purpose consistency: "
        +
        purpose_result.get(
            "reason",
            "Unknown"
        )

        +

        " | Geo/time: "
        +
        geo_result.get(
            "reason",
            "Unknown"
        )

        +

        f" | Combined risk: "
        f"{combined_risk}/100"
    )


    return {

        "result":
            final_result,

        "confidence":
            confidence,

        "risk_score":
            combined_risk,

        "purpose_result":
            purpose_status,

        "purpose_confidence":
            round(
                purpose_confidence,
                4
            ),

        "reason":
            reason,

        "recommendation":
            recommendation
    }