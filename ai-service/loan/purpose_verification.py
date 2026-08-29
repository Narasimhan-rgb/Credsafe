# loan/purpose_verification.py

from pathlib import Path
from PIL import Image

_model = None


# =========================================================
# LOAD CLIP ONLY WHEN NEEDED
# =========================================================

def get_classifier():

    global _model

    if _model is None:

        from transformers import pipeline

        print(
            "Loading CLIP purpose verification model..."
        )

        _model = pipeline(
            task="zero-shot-image-classification",
            model="openai/clip-vit-base-patch32"
        )

        print(
            "CLIP purpose verification model loaded."
        )

    return _model


# =========================================================
# PURPOSE → EXPECTED VISUAL OBJECTS
# =========================================================

PURPOSE_LABELS = {

    "BUSINESS_EQUIPMENT": [
        "business equipment",
        "office equipment",
        "industrial machinery",
        "computer equipment",
        "shop equipment",
        "commercial equipment"
    ],

    "VEHICLE": [
        "car",
        "motorcycle",
        "commercial vehicle",
        "delivery vehicle",
        "auto rickshaw"
    ],

    "AGRICULTURE": [
        "tractor",
        "agricultural equipment",
        "farm machinery",
        "irrigation equipment",
        "farming tools"
    ],

    "LIVESTOCK": [
        "cow",
        "buffalo",
        "goat",
        "sheep",
        "livestock"
    ],

    "SHOP": [
        "retail shop",
        "store equipment",
        "shop shelves",
        "cash register",
        "commercial refrigerator"
    ],

    "EDUCATION": [
        "computer",
        "laptop",
        "books",
        "educational equipment",
        "study equipment"
    ],

    "HOME_EQUIPMENT": [
        "home appliance",
        "sewing machine",
        "furniture",
        "household equipment"
    ]
}


# Objects deliberately unrelated to most loan purposes.
DISTRACTOR_LABELS = [

    "selfie of a person",

    "landscape",

    "food",

    "pet",

    "random document",

    "empty room",

    "street",

    "screenshot"
]


# =========================================================
# DETECT PURPOSE CATEGORY
# =========================================================

def detect_purpose_category(
    loan_purpose: str | None
) -> str:

    if not loan_purpose:

        return "UNKNOWN"

    text = loan_purpose.lower()

    # ---------------------------------------------
    # BUSINESS EQUIPMENT
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "business equipment",
            "machinery",
            "machine",
            "equipment",
            "computer",
            "commercial equipment"
        ]
    ):

        return "BUSINESS_EQUIPMENT"

    # ---------------------------------------------
    # VEHICLE
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "vehicle",
            "car",
            "bike",
            "motorcycle",
            "auto",
            "rickshaw"
        ]
    ):

        return "VEHICLE"

    # ---------------------------------------------
    # AGRICULTURE
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "agriculture",
            "agricultural",
            "tractor",
            "farm",
            "irrigation"
        ]
    ):

        return "AGRICULTURE"

    # ---------------------------------------------
    # LIVESTOCK
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "livestock",
            "cow",
            "buffalo",
            "goat",
            "sheep",
            "dairy"
        ]
    ):

        return "LIVESTOCK"

    # ---------------------------------------------
    # SHOP
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "shop",
            "store",
            "retail"
        ]
    ):

        return "SHOP"

    # ---------------------------------------------
    # EDUCATION
    # ---------------------------------------------

    if any(
        word in text
        for word in [
            "education",
            "study",
            "college",
            "school",
            "laptop"
        ]
    ):

        return "EDUCATION"

    return "UNKNOWN"


# =========================================================
# VERIFY PURPOSE AGAINST IMAGE
# =========================================================

def verify_purpose_consistency(

    file_path: str,

    loan_purpose: str | None

) -> dict:

    path = Path(file_path)

    # -----------------------------------------------------
    # FILE VALIDATION
    # -----------------------------------------------------

    if not path.exists():

        return {

            "result": "MISMATCH",

            "confidence": 0.99,

            "purpose_category": "UNKNOWN",

            "detected_label": None,

            "reason":
                "Evidence image could not be found"
        }

    # -----------------------------------------------------
    # PURPOSE CATEGORY
    # -----------------------------------------------------

    category = detect_purpose_category(
        loan_purpose
    )

    if category == "UNKNOWN":

        return {

            "result":
                "MANUAL_REVIEW",

            "confidence":
                0.50,

            "purpose_category":
                "UNKNOWN",

            "detected_label":
                None,

            "reason":
                "Loan purpose could not be mapped "
                "to a supported visual category"
        }

    expected_labels = (
        PURPOSE_LABELS[
            category
        ]
    )

    candidate_labels = (

        expected_labels

        +

        DISTRACTOR_LABELS
    )

    try:

        # -------------------------------------------------
        # OPEN IMAGE
        # -------------------------------------------------

        image = Image.open(
            path
        ).convert(
            "RGB"
        )

        # -------------------------------------------------
        # CLIP ZERO-SHOT CLASSIFICATION
        # -------------------------------------------------

        classifier = get_classifier()

        predictions = classifier(

            image,

            candidate_labels=
                candidate_labels
        )

        # -------------------------------------------------
        # FIND TOP RESULT
        # -------------------------------------------------

        top_prediction = (
            predictions[0]
        )

        top_label = (
            top_prediction[
                "label"
            ]
        )

        top_score = float(
            top_prediction[
                "score"
            ]
        )

        # -------------------------------------------------
        # BEST EXPECTED PURPOSE SCORE
        # -------------------------------------------------

        expected_predictions = [

            prediction

            for prediction
            in predictions

            if prediction["label"]
            in expected_labels
        ]

        expected_predictions.sort(

            key=lambda item:
                item["score"],

            reverse=True
        )

        best_expected = (
            expected_predictions[0]
        )

        expected_label = (
            best_expected[
                "label"
            ]
        )

        expected_score = float(
            best_expected[
                "score"
            ]
        )

        # -------------------------------------------------
        # PURPOSE CONSISTENCY DECISION
        # -------------------------------------------------

        if (
            top_label in expected_labels
            and
            expected_score >= 0.35
        ):

            result = "MATCH"

            reason = (

                f"Image is visually consistent "
                f"with loan purpose. "
                f"Detected '{expected_label}'."
            )

        elif expected_score >= 0.20:

            result = "PARTIAL_MATCH"

            reason = (

                f"Image has partial visual "
                f"consistency with the loan purpose. "
                f"Possible object: "
                f"'{expected_label}'."
            )

        else:

            result = "MISMATCH"

            reason = (

                f"Image does not appear consistent "
                f"with the stated loan purpose. "
                f"Strongest visual label: "
                f"'{top_label}'."
            )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return {

            "result":
                result,

            "confidence":
                round(
                    expected_score,
                    4
                ),

            "purpose_category":
                category,

            "detected_label":
                top_label,

            "detected_score":
                round(
                    top_score,
                    4
                ),

            "expected_label":
                expected_label,

            "expected_score":
                round(
                    expected_score,
                    4
                ),

            "reason":
                reason
        }

    except Exception as exc:

        print(
            "Purpose verification error:",
            exc
        )

        return {

            "result":
                "MANUAL_REVIEW",

            "confidence":
                0.0,

            "purpose_category":
                category,

            "detected_label":
                None,

            "reason":
                "Purpose verification model "
                f"failed: {exc}"
        }