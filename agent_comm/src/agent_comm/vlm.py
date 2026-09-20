# agent_comm/vlm.py
import base64
import openai


class VLM:
    """
    Simple VLM wrapper that mirrors agent_comm.llm.LLM, but accepts an image (as base64)
    alongside the text prompt and calls OpenAI's chat.completions with image input.
    """

    def __init__(
        self,
        model: str,
        base_url: str,
        temperature: float,
        timeout: float,
        api_key: str,
    ) -> None:
        self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.timeout = timeout

    def _to_data_url(self, b64_bytes: bytes, mime: str = "image/jpeg") -> str:
        # Accepts raw base64 bytes; returns a data URL suitable for image input
        b64_str = b64_bytes.decode("utf-8")
        return f"data:{mime};base64,{b64_str}"

    def __call__(self, prompt: str, image_b64: bytes, mime: str = "image/jpeg") -> str:
        """
        prompt: user text
        image_b64: base64-encoded image BYTES (not the raw image). e.g., base64.b64encode(jpeg_bytes)
        mime: MIME type string for the image (default: image/jpeg)
        """
        data_url = self._to_data_url(image_b64, mime=mime)

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ],
                }
            ],
            temperature=self.temperature,
            timeout=self.timeout,
        )
        return resp.choices[0].message.content
