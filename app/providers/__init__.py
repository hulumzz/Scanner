from app.core.config import get_settings
from app.providers.base import VisionProvider
from app.providers.groq import GroqVisionProvider
from app.providers.gemini import GeminiVisionProvider


def get_vision_provider() -> VisionProvider:
    name = get_settings().vision_provider.lower()
    if name == 'groq': return GroqVisionProvider()
    if name == 'gemini': return GeminiVisionProvider()
    raise ValueError(f'Unsupported VISION_PROVIDER: {name}')
