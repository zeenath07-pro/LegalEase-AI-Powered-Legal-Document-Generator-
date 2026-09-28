
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

VALID = {
    "document_type": "NDA",
    "parties": "Company A and Company B",
    "terms": "Keep information confidential",
    "dates": "2027-01-01",
}


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_mocked():
    with patch(
        "backend.routes.GeminiDocumentGenerator.generate_document",
        return_value="NON-DISCLOSURE AGREEMENT\n1. Confidentiality",
    ):
        response = client.post(
            "/generate",
            json=VALID,
        )

    assert response.status_code == 200
    assert "Confidentiality" in response.json()["document"]


def test_validation():
    response = client.post(
        "/generate",
        json={
            **VALID,
            "parties": "",
        },
    )

    assert response.status_code == 422


def test_missing_key():
    with patch.dict(
        "os.environ",
        {"GEMINI_API_KEY": ""},
    ):
        response = client.post(
            "/generate",
            json=VALID,
        )

    assert response.status_code == 503