from pathlib import Path
from PIL import Image


def verify_image(
    file_path: str,
    loan_purpose: str | None = None
) -> dict:

    path = Path(file_path)

    if not path.exists():
        return {
            "result": "REJECTED",
            "confidence": 0.99,
            "reason": "Evidence file does not exist",
            "recommendation": "REQUEST_NEW_EVIDENCE"
        }

    try:
        with Image.open(path) as image:
            width, height = image.size
            image_format = image.format

        if width < 200 or height < 200:
            return {
                "result": "SUSPICIOUS",
                "confidence": 0.82,
                "reason": "Image resolution is too low for reliable verification",
                "recommendation": "MANUAL_REVIEW"
            }

        return {
            "result": "VALID",
            "confidence": 0.91,
            "reason": (
                f"Image is readable and structurally valid "
                f"({image_format}, {width}x{height})"
            ),
            "recommendation": "OFFICER_REVIEW"
        }

    except Exception as exc:
        return {
            "result": "REJECTED",
            "confidence": 0.95,
            "reason": f"Unable to read image: {exc}",
            "recommendation": "REQUEST_NEW_EVIDENCE"
        }