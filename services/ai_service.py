"""AI listing service logic."""

import base64
from io import BytesIO
import json
import logging
from typing import Any, Dict, List, Mapping, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import current_app
from PIL import Image
from werkzeug.datastructures import FileStorage

from services.base_service import BaseService
from services.listing_service import listing_service

logger = logging.getLogger(__name__)
DEFAULT_AI_DRAFT_ERROR = "We could not generate a draft from this image right now."

AI_DRAFT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "suggested_title": {"type": "STRING"},
        "suggested_category": {"type": "STRING"},
        "suggested_description": {"type": "STRING"},
        "visible_text": {"type": "ARRAY", "items": {"type": "STRING"}},
        "detected_attributes": {"type": "ARRAY", "items": {"type": "STRING"}},
        "confidence": {
            "type": "STRING",
            "enum": ["high", "medium", "low"],
        },
    },
    "required": [
        "suggested_title",
        "suggested_category",
        "suggested_description",
        "visible_text",
        "detected_attributes",
        "confidence",
    ],
}
AI_GENERATION_CONFIG = {
    "temperature": 0.2,
    "maxOutputTokens": 300,
    "responseMimeType": "application/json",
    "responseSchema": AI_DRAFT_SCHEMA,
}


class AIListingService(BaseService):
    """Handle AI-assisted listing generation."""

    def generate_listing_draft(
        self,
        image_file: Optional[FileStorage],
    ) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
        """Generate a normalized listing draft from one uploaded image."""
        validation_error = self._validate_image_file(image_file)
        if validation_error is not None:
            return False, validation_error, None

        provider = current_app.config["AI_PROVIDER"]
        if provider != "gemini":
            return False, "The configured AI provider is not supported.", None

        image_bytes = image_file.read()
        image_file.stream.seek(0)
        if not image_bytes:
            return False, "The uploaded image could not be read.", None

        # Send a smaller analysis copy to Gemini so large camera images do not block the draft flow.
        image_bytes, ai_mime_type = self._prepare_image_for_ai(image_bytes)

        try:
            draft = self._generate_with_gemini(image_bytes, ai_mime_type)
        except ValueError as error:
            return False, str(error), None
        except HTTPError as error:
            self._log_http_error(error, "Gemini HTTP error while generating listing draft.")
            return False, DEFAULT_AI_DRAFT_ERROR, None
        except (URLError, TimeoutError) as error:
            logger.warning("Primary Gemini model failed; retrying with fallback model.")
            try:
                # Retry once with a fallback model because image latency is inconsistent in free-tier usage.
                draft = self._generate_with_gemini(
                    image_bytes,
                    ai_mime_type,
                    model_name=current_app.config["GEMINI_FALLBACK_MODEL"],
                )
            except ValueError as fallback_error:
                return False, str(fallback_error), None
            except HTTPError as fallback_http_error:
                self._log_http_error(
                    fallback_http_error,
                    "Gemini HTTP error while retrying listing draft.",
                )
                return False, DEFAULT_AI_DRAFT_ERROR, None
            except (URLError, TimeoutError):
                logger.exception(
                    "Gemini network error while retrying listing draft after primary failure: %s",
                    error,
                )
                return False, DEFAULT_AI_DRAFT_ERROR, None

        return True, None, draft

    def _prepare_image_for_ai(self, image_bytes: bytes) -> Tuple[bytes, str]:
        """Resize the uploaded image for faster AI analysis without changing the final upload."""
        max_dimension = current_app.config["AI_IMAGE_MAX_DIMENSION"]
        with Image.open(BytesIO(image_bytes)) as image:
            image = image.convert("RGB")
            image.thumbnail((max_dimension, max_dimension))
            optimized_buffer = BytesIO()
            image.save(optimized_buffer, format="JPEG", quality=85, optimize=True)
        return optimized_buffer.getvalue(), "image/jpeg"

    def _generate_with_gemini(
        self,
        image_bytes: bytes,
        mime_type: str,
        model_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Call the Gemini API and normalize the returned JSON draft."""
        api_key = current_app.config.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("AI draft generation is not configured yet.")

        model_name = model_name or current_app.config["GEMINI_MODEL"]
        allowed_categories = listing_service.get_category_options()
        allowed_category_names = [category["name"] for category in allowed_categories]
        prompt = self._build_listing_prompt(allowed_category_names)
        # Gemini structured output keeps the form-filling response predictable for the frontend.
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(image_bytes).decode("utf-8"),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": AI_GENERATION_CONFIG,
        }
        request = Request(
            (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={api_key}"
            ),
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        timeout = current_app.config["AI_REQUEST_TIMEOUT_SECONDS"]
        with urlopen(request, timeout=timeout) as response:
            response_payload = json.loads(response.read().decode("utf-8"))

        response_text = self._extract_response_text(response_payload)
        return self._normalize_draft_payload(json.loads(response_text), allowed_category_names)

    @staticmethod
    def _validate_image_file(image_file: Optional[FileStorage]) -> Optional[str]:
        """Ensure one readable image file was provided."""
        if image_file is None or not image_file.filename:
            return "Please upload one product image first."
        if not (image_file.mimetype or "").startswith("image/"):
            return "Please upload a valid image file."
        return None

    @staticmethod
    def _build_listing_prompt(allowed_categories: List[str]) -> str:
        """Create the constrained marketplace prompt for Gemini."""
        return (
            "You are an assistant that helps users create accurate and editable listing drafts "
            "for a New Zealand second-hand marketplace.\n"
            "Analyse the uploaded product image and return JSON only.\n"
            "The output should help pre-fill a user-editable listing form for a second-hand "
            "marketplace.\n"
            "Tasks:\n"
            "1. Identify the main item in the image.\n"
            "2. Extract any clearly visible text that helps identify the item or bundled "
            "contents.\n"
            "3. Suggest a short marketplace-style title.\n"
            "4. Choose exactly one category from the allowed category list.\n"
            "5. Write a structured marketplace-style description:\n"
            '   - begin with one short sentence describing the main item\n'
            '   - if clearly visible accessories or bundled items are present, list them under '
            '"Includes:"\n'
            "   - keep the wording factual, clear, and easy for the user to edit\n"
            "   - keep the description concise and do not exceed 3 short sections or lines\n"
            "6. List up to 5 detected visual attributes.\n"
            "7. Set confidence to high, medium, or low based on how clearly the main item can "
            "be identified.\n"
            "Rules:\n"
            "Use only information that is clearly visible in the image.\n"
            "Do not infer or guess any information that is not clearly visible in the image.\n"
            "Do not include assumptions about condition, quality, size, specifications, "
            "performance, completeness, or usability unless they are directly supported by "
            "visible evidence.\n"
            "Do not invent brand, model, accessories, bundled contents, or claims that are not "
            "clearly visible.\n"
            "If something cannot be confirmed from the image, leave it out.\n"
            "If visible text helps identify the item, use it.\n"
            "Do not repeat long blocks of visible text in the description unless they help "
            "identify the item or bundled contents.\n"
            "Keep visible_text concise and include only the most useful text for identifying the "
            "item or bundled contents.\n"
            "Choose the most specific suitable category from the allowed category list.\n"
            "If the exact category is uncertain, choose Other.\n"
            "The category must be one of the allowed categories.\n"
            "Return only the schema fields and do not include any extra commentary outside the "
            "JSON object.\n"
            "Return valid JSON only.\n"
            f"Allowed categories: {', '.join(allowed_categories)}"
        )

    @staticmethod
    def _extract_response_text(response_payload: Mapping[str, Any]) -> str:
        """Read the JSON text from the Gemini response payload."""
        candidates = response_payload.get("candidates", [])
        if not candidates:
            raise ValueError("The AI service did not return a draft.")

        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts or "text" not in parts[0]:
            raise ValueError("The AI draft response was incomplete.")
        return parts[0]["text"]

    def _normalize_draft_payload(
        self,
        draft_payload: Mapping[str, Any],
        allowed_category_names: List[str],
    ) -> Dict[str, Any]:
        """Validate and normalize model output into the app's expected draft shape."""
        suggested_category = str(draft_payload.get("suggested_category", "")).strip()
        if suggested_category not in allowed_category_names:
            suggested_category = "Other"

        confidence = str(draft_payload.get("confidence", "medium")).strip().lower()
        if confidence not in {"high", "medium", "low"}:
            confidence = "medium"

        return {
            "suggested_title": str(draft_payload.get("suggested_title", "")).strip() or "Untitled Item",
            "suggested_category": suggested_category,
            "suggested_description": (
                str(draft_payload.get("suggested_description", "")).strip()
                or "Please review and complete the item details."
            ),
            "visible_text": self._clean_string_list(draft_payload.get("visible_text", [])),
            "detected_attributes": self._clean_string_list(
                draft_payload.get("detected_attributes", [])
            ),
            "confidence": confidence,
        }

    @staticmethod
    def _log_http_error(error: HTTPError, message: str) -> None:
        """Log an HTTP error and its response body when Gemini rejects a request."""
        logger.exception(message)
        try:
            error_body = error.read().decode("utf-8", errors="ignore")
            logger.error("Gemini response body: %s", error_body)
        except Exception:  # pragma: no cover - best effort logging only
            logger.exception("Failed to read Gemini HTTP error body.")

    @staticmethod
    def _clean_string_list(raw_values: Any) -> List[str]:
        """Return a trimmed list of non-empty strings."""
        if not isinstance(raw_values, list):
            return []
        cleaned_values = []
        for raw_value in raw_values:
            cleaned_value = str(raw_value).strip()
            if cleaned_value:
                cleaned_values.append(cleaned_value)
        return cleaned_values


ai_listing_service = AIListingService()
