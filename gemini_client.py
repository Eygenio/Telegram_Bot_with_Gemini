import logging
import time
from typing import List, Dict
from google import genai
from google.genai.errors import ServerError

from config import Config

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class GeminiClient:
    """Клиент для Google Gemini, использующий models.generate_content.

    Формат contents:
    [
      {"role": "user", "parts": [{"text": "..."}]},
      {"role": "model", "parts": [{"text": "..."}]},
      ...
    ]

    Поддерживается повтор попыток при 503.
    """

    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = Config.GEMINI_MODEL

    def ask(self, contents: List[Dict], retries: int = 4, backoff: float = 1.5) -> str:
        attempt = 0
        while attempt <= retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                )
                return response.text

            except ServerError as e:
                msg = str(e)
                # Попытка поймать 503
                if "503" in msg or "UNAVAILABLE" in msg or getattr(e, 'status_code', None) == 503:
                    wait = backoff * (attempt + 1)
                    logger.warning(f"Gemini overloaded (503). Retry {attempt+1}/{retries} after {wait}s")
                    time.sleep(wait)
                    attempt += 1
                    continue
                logger.error(f"Gemini ServerError: {e}")
                raise
            except Exception as e:
                logger.error(f"Ошибка при обращении к Gemini: {e}")
                raise

        raise Exception("Gemini API недоступен после нескольких попыток")
