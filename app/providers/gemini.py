from app.providers.base import VisionProvider, VisionResult
from app.core.exceptions import ScannerError


class GeminiVisionProvider(VisionProvider):
    async def extract_json(self, image_bytes: bytes, mime_type: str, prompt: str) -> VisionResult:
        raise ScannerError('AI_INVALID_RESPONSE', 'Gemini provider belum diaktifkan untuk KK nyata pada V1.', 501)
