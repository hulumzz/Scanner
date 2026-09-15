import base64
import json
import httpx
from app.core.config import get_settings
from app.core.exceptions import ScannerError
from app.providers.base import VisionProvider, VisionResult


class GroqVisionProvider(VisionProvider):
    endpoint = 'https://api.groq.com/openai/v1/chat/completions'

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.groq_api_key:
            raise ScannerError('AI_INVALID_RESPONSE', 'GROQ_API_KEY belum dikonfigurasi.', 503)

    async def extract_json(self, image_bytes: bytes, mime_type: str, prompt: str) -> VisionResult:
        image_b64 = base64.b64encode(image_bytes).decode('ascii')
        payload = {'model': self.settings.vision_model, 'temperature': 0, 'response_format': {'type': 'json_object'}, 'messages': [{'role': 'user', 'content': [{'type': 'text', 'text': prompt}, {'type': 'image_url', 'image_url': {'url': f'data:{mime_type};base64,{image_b64}'}}]}]}
        try:
            async with httpx.AsyncClient(timeout=self.settings.ai_timeout_seconds) as client:
                response = await client.post(self.endpoint, headers={'Authorization': f'Bearer {self.settings.groq_api_key}', 'Content-Type': 'application/json'}, json=payload)
        except httpx.TimeoutException as exc:
            raise ScannerError('AI_TIMEOUT', 'Layanan AI melewati batas waktu.', 504) from exc
        if response.status_code == 429: raise ScannerError('AI_RATE_LIMIT', 'Layanan AI sedang membatasi permintaan.', 429)
        if response.status_code >= 400: raise ScannerError('AI_INVALID_RESPONSE', f'Layanan AI mengembalikan HTTP {response.status_code}.', 502)
        try:
            body = response.json(); content = body['choices'][0]['message']['content']; data = json.loads(content) if isinstance(content, str) else content; usage = body.get('usage', {})
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise ScannerError('AI_INVALID_RESPONSE', 'JSON dari AI tidak dapat diparsing.', 502) from exc
        return VisionResult(data=data, metadata={'request_id': response.headers.get('x-request-id'), 'usage': usage})
