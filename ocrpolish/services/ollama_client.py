import json
import logging
import re
from typing import TypeVar

from ollama import Client
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model: str = "gemma4:26b", host: str = "http://localhost:11434"):
        self.model = model
        self.client = Client(host=host)

    def extract_structured(self, prompt: str, schema: type[T], retries: int = 3) -> T:
        """
        Sends a prompt to Ollama and returns a validated Pydantic model.
        Includes retry logic for validation errors.
        """
        attempt = 0
        last_error = None
        
        while attempt <= retries:
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a specialized metadata extraction assistant. "
                                "Extract requested fields accurately and respond "
                                "strictly in JSON format matching the schema."
                            ),
                        },
                        {
                            "role": "user",
                            "content": (
                                f"{prompt}\n\nStrictly follow this JSON schema:\n"
                                f"{json.dumps(schema.model_json_schema(), indent=2)}"
                            ),
                        },
                    ],
                    format=schema.model_json_schema(),
                    options={"temperature": 0},
                )
                
                content = response["message"]["content"].strip()
                
                # Defensively strip markdown code blocks if the model ignored the format constraint
                if content.startswith("```"):
                    # Remove opening block
                    content = re.sub(r"^```(?:json)?\s*", "", content)
                    # Remove closing block
                    content = re.sub(r"\s*```$", "", content)
                
                return schema.model_validate_json(content)
            except ValidationError as e:
                attempt += 1
                last_error = e
                logger.warning(f"Schema validation failed on attempt {attempt}: {e}")
                if attempt <= retries:
                    prompt += (
                        f"\n\nIMPORTANT: Previous response failed validation: {e}. "
                        "Please ensure the output strictly matches the schema."
                    )
            except Exception as e:
                logger.error(f"Ollama API error: {e}")
                raise

        logger.error(f"Failed extraction after {retries + 1} attempts.")
        raise last_error if last_error else Exception("Extraction failed")
