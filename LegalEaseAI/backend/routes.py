
import logging

from fastapi import APIRouter, HTTPException

from backend.schemas import DocumentRequest, DocumentResponse
from backend.ai_core.gemini_generator import GeminiDocumentGenerator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/generate", response_model=DocumentResponse)
def generate_document(payload: DocumentRequest):
    try:
        generator = GeminiDocumentGenerator()
        document = generator.generate_document(payload)

        return DocumentResponse(document=document)

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception("Document generation failed")

        raise HTTPException(
            status_code=502,
            detail=(
                "AI service failed. Check your API key, "
                "model, quota and internet connection."
            ),
        ) from exc