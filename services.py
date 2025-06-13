import asyncio
from functools import lru_cache
import os
import time
import anyio
from typing import Dict, Any, List, Tuple
from models import PositionDTO
from groq import Groq, RateLimitError  # Ensure you have this package installed
from output_models import CVEvaluationResultDTO
from pydantic import ValidationError

class Evaluator:
    def __init__(
        self,
        api_keys: List[str],
        model: str = "gemma2-9b-it",
        max_completion_tokens: int = 1024,
        token_limit: int = 15000,
        window_sec: int = 60,

    ):
        self.api_keys = api_keys
        self.model = model
        self.max_tokens = max_completion_tokens
        self.token_limit = token_limit
        self.window_sec = window_sec

    
    def _build_messages(self, cv_text: str, position: PositionDTO) -> List[Dict]:
        return [
            {
                "role": "system",
                "content": "You are an expert CV Evaluator.\nRead the given CV ( text ) and Position ( JSON ) and print the Evaluation Response ( OUTPUT SCHEMA ).\n\nOUTPUT SCHEMA\n{\n  \"candidateName\": <string>,\n  \"requiredSkills\": { \"scraped\": [<string>, …], \"score\": <0-100> },\n  \"niceToHave\":    { \"scraped\": [<string>, …], \"score\": <0-100> },\n  \"languages\":     { \"value\": [<string>, …], \"score\": <0-100> },\n  \"certifications\":{ \"scraped\": [<string>, …], \"score\": <0-100> },\n  \"responsibilities\":{ \"scraped\": [<string>, …], \"score\": <0-100> },\n  \"minimumExperienceMonths\":{ \"value\": <int>, \"score\": <0-100> },\n  \"level\": { \"value\": \"<Intern|Junior|Mid|Senior|Lead>\", \"score\": <0-100> },\n  \"minimumEducationLevel\":{ \"value\": \"<HighSchool|Bachelor|Master|Doctorate>\", \"score\": <0-100> }\n}\n\n\nRULES\n\n• For each field (candidateSkills, niceToHave, responsibilities):\n  – “scraped”: include only those items from the CV that match (lexically or semantically) items in the corresponding field of the Position.\n  – Do not include any CV items in “scraped” that do not have an equivalent in the Position.\n  – score = round((number of matched items) / (number of items required by the Position) × 100). If no similarity score = 0\n\n• For certifications:\n  – “scraped”: include only those certification names from the CV that match (lexically or semantically) the certifications listed in the Position.\n  – Treat equivalent phrasing or abbreviations as valid matches (e.g., “UiPath Certified Professional Associate RPA Developer” ≈ “UiPath Certified RPA Associate”).\n  – score = 100 if all required certifications are semantically matched, regardless of any extra certifications present in the CV; otherwise round((number of matched certifications) / (number of certifications required by the Position) × 100).\n\n• For languages:\n  – “value”: include only languages that appear in both the CV and the Position’s “languages” list.\n  – score = 100 if all languages required by the Position are found in the CV; otherwise round((number of matched languages) / (number of required languages) × 100).\n\n• For minimumExperienceMonths:\n  – “value”: total months of experience extracted from the CV.\n  – score = 100 if value ≥ Position.minimumExperienceMonths; otherwise round((value / Position.minimumExperienceMonths) × 100).\n\n• For level:\n  – “value”: extract from the CV the level that corresponds to one of: Intern, Junior, Mid, Senior, or Lead.\n  – score = 100 if the extracted level is equal to or higher than the Position.level; otherwise assign a proportionally lower score.\n\n• For minimumEducationLevel:\n  – “value”: extract from the CV the highest education level (HighSchool, Bachelor, Master, or Doctorate).\n  – score = 100 if the extracted education level is equal to or higher than Position.minimumEducationLevel; otherwise assign a proportionally lower score."
            },
            {
                "role": "user",
                "content": (
                    f"A. CV :\n{cv_text}\n\n"
                    f"B. Position :\n{position.json()}"
                )
            }
        ]
  
    def _sync_worker(
        self,
        cv_text: str,
        position: PositionDTO,
        api_key: str,
    ) -> Tuple[CVEvaluationResultDTO, int]:
        """
        Funcție sincronică privată: apelează API-ul și parsează răspunsul.
        Returnează (DTO, total_tokens).
        """
        client = Groq(api_key=api_key)
        messages = self._build_messages(cv_text, position)
        resp = client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_completion_tokens=self.max_tokens,
            top_p=0.95,
            stream=False,
            response_format={"type": "json_object"},
            seed=12345,
        )
        content = resp.choices[0].message.content
        try:
            dto = CVEvaluationResultDTO.model_validate_json(content)
        except ValidationError as e:
            dto = CVEvaluationResultDTO()
            dto.candidateName = "Error parsing LLM"
            print(f"Validation error: {e}")
        return dto, resp.usage.total_tokens
    
    
    def evaluate(self, cv_text: str, position: PositionDTO) -> CVEvaluationResultDTO:
        """
        Evaluare sincronă pentru un singur CV.
        """
        dto, _ = self._sync_worker(cv_text, position, self.api_keys[0])
        return dto
  
    async def evaluate_bulk(
        self,
        cv_texts: List[str],
        position: PositionDTO,
    ) -> List[CVEvaluationResultDTO]:
        """
        Evaluare concurrentă a unei liste de CV-uri, folosind round-robin pe chei.
        """
        key_queue: asyncio.Queue = asyncio.Queue()
        for key in self.api_keys:
            key_queue.put_nowait(key)

        per_key_state: Dict[str, Dict[str, Any]] = {
            key: {"window_start": time.monotonic(), "tokens": 0}
            for key in self.api_keys
        }
        print(per_key_state)
        cond = asyncio.Condition()

        results: List[CVEvaluationResultDTO] = [None] * len(cv_texts)

        async def _worker(idx: int, cv: str):
            print(f"[{idx+1}] Task pending…")
            api_key = await key_queue.get()
            state = per_key_state[api_key]
            try:
                # Așteaptă buget
                while True:
                    async with cond:
                        now = time.monotonic()
                        elapsed = now - state["window_start"]
                        if elapsed >= self.window_sec:
                            state["window_start"] = now
                            state["tokens"] = 0
                            cond.notify_all()
                        if state["tokens"] + self.max_tokens <= self.token_limit:
                            state["tokens"] += self.max_tokens
                            break
                        to_wait = self.window_sec - elapsed
                        print(f"[{idx+1}] ⏳ Key {api_key} exhausted ({state['tokens']} tokens), sleeping {to_wait:.1f}s")

                    await asyncio.sleep(to_wait)

                # Apel cu retry
                attempt = 0
                while attempt < 3:
                    attempt += 1
                    try:
                        print(f"[{idx+1}] ▶️ Using {api_key} to eval CV (attempt {attempt})…")

                        dto, used = await anyio.to_thread.run_sync(
                            lambda: self._sync_worker(cv, position, api_key)
                        )

                        print(f"[{idx+1}] ← {used} tokens used on {api_key}")

                        break
                    except RateLimitError:
                        print(f"[{idx+1}] ⚠️ RateLimitError on {api_key}, retrying in 10s…")
                        await asyncio.sleep(10)
                    except Exception as e:
                        # Dacă vrei să faci același back-off la orice eroare:
                        print(f"[{idx+1}] ⚠️ Unexpected error: {e}, retrying in 10s…")
                        await asyncio.sleep(10)

                # Ajustează consum și eliberează cheie
                async with cond:
                    state["tokens"] -= (self.max_tokens - used)
                    print(f"    [{api_key}] Window now at {state['tokens']} tokens")
                    cond.notify_all()
                results[idx] = dto
            finally:
                key_queue.put_nowait(api_key)

        tasks = [asyncio.create_task(_worker(i, cv)) for i, cv in enumerate(cv_texts)]
        await asyncio.gather(*tasks)
        return results
