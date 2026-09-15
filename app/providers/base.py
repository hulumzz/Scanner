from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class VisionResult:
    data: dict
    metadata: dict


class VisionProvider(ABC):
    @abstractmethod
    async def extract_json(self, image_bytes: bytes, mime_type: str, prompt: str) -> VisionResult:
        raise NotImplementedError
