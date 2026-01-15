import time
from google import genai
from google.genai.errors import ClientError, ServerError

SYSTEM_PROMPT = """
You are Ali AI v0.1.

Rules:
- You are NOT Google, NOT Gemini.
- You were created by Ali.
- If asked "who are you", say:
  "Men Ali AI v0.1 — Ali tomonidan yaratilgan sun’iy intellektman."
- Answer in Uzbek unless user asks otherwise.
- You may use Markdown formatting.
"""

class GeminiPool:
    def __init__(self, keys: list[str]):
        if not keys:
            raise ValueError("Gemini API keylar topilmadi")
        self.keys = keys
        self.index = 0
        self.dead_keys = set()

    def _client(self):
        return genai.Client(api_key=self.keys[self.index])

    def _next_key(self):
        self.dead_keys.add(self.index)

        for _ in range(len(self.keys)):
            self.index = (self.index + 1) % len(self.keys)
            if self.index not in self.dead_keys:
                print(f"API key {self.index} ga o‘tildi")
                return

        # HAQIQATAN hammasi tugagan
        raise RuntimeError("Hozir barcha API keylar limitda. Keyinroq urinib ko‘ring.")

    def generate(self, user_prompt: str) -> str:
        final_prompt = f"{SYSTEM_PROMPT}\n\nUser:\n{user_prompt}"

        attempts = 0
        max_attempts = len(self.keys) * 3

        while attempts < max_attempts:
            try:
                client = self._client()
                res = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=final_prompt
                )
                return res.text

            except ClientError as e:
                # 429 — quota tugagan
                if getattr(e, "status_code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e):
                    print(f"API key {self.index} limiti tugadi → almashtirildi")
                    self._next_key()
                    attempts += 1
                    continue
                raise e

            except ServerError:
                # 503 — model band (KEYNI O‘LDIRMAYMIZ)
                print("Model band (503). 2 soniya kutyapman...")
                time.sleep(2)
                attempts += 1
                continue

        return "⏳ Ali AI hozir band. Iltimos, birozdan keyin qayta urinib ko‘ring."
