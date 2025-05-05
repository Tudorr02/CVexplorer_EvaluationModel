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



# @lru_cache
# def _client() -> Groq:
#     import os
#     # return Groq(api_key=os.getenv("GROQ_API_KEY"))
#     return Groq(api_key="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")



# def evaluate(cv_text: str, position: PositionDTO) -> Dict[str, Any]:
#     client = _client()
#     # Construct the messages for the chat completion request.
#     messages = [
#         {
#             "role": "system",
#             "content": (
#                 "You are an expert resume analyzer. Your task is to analyze the CV (A. given as plain text) "
#                 "along with the Position (B. given as JSON) and extract the following fields. For each field, also compute a score "
#                 "(a percentage from 0 to 100) representing how closely the candidate's CV matches the corresponding value in the Position JSON.\n\n"
#                 "Rules:\n\n"
#                 "1. Only extract information from the provided CV text.\n"
#                 "2. If a field cannot be determined, output an empty list for list fields, or a zero value (and a score of 0) for numeric values.\n"
#                 "3. The final answer must be output strictly in JSON format, with keys corresponding exactly to the field names above.\n"
#                 "4. Use the following JSON structure for your output:\n"
#                 "{\n"
#                 "  \"candidateName\" : <str>\n"
#                 "  \"requiredSkills\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"niceToHave\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"languages\": {\n"
#                 "    \"value\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"certifications\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"responsibilities\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"minimumExperienceMonths\": {\n"
#                 "    \"value\": <number>,\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"level\": {\n"
#                 "    \"value\": \"<one of Intern, Junior, Mid, Senior, Lead>\",\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"minimumEducationLevel\": {\n"
#                 "    \"value\": \"<one of HighSchool, Bachelor, Master, Doctorate>\",\n"
#                 "    \"score\": <number>\n"
#                 "  }\n"
#                 "}\n"
#             )
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"A. CV :\n{cv_text}\n\n"
#                 f"B. Position :\n{position.json()}"
#             )
#         }
#     ]

#     # Create the chat completion by calling the Groq API
#     completion = client.chat.completions.create(
#         model="gemma2-9b-it",
#         messages=messages,
#         temperature=0.3,
#         max_completion_tokens=1024,
#         top_p=0.8,
#         stream=False,
#         response_format={"type": "json_object"},
#         stop=None,
#         seed=12345,
#     )

#     # Assuming the returned structure contains the analysis in completion.choices[0].message
#     result_str = completion.choices[0].message.content
#      # Validate and parse the JSON output using the ResumeAnalysisResult model
#     try:
#         analysis_result = CVEvaluationResultDTO.model_validate_json(result_str)
#     except ValidationError as e:
#         raise Exception(f"Validation error: {e}")

#     return analysis_result




# def _build_messages(cv_text: str, position: PositionDTO) -> List[Dict]:
#     return [
#          {
#             "role": "system",
#             "content": (
#                 "You are an expert resume analyzer. Your task is to analyze the CV (A. given as plain text) "
#                 "along with the Position (B. given as JSON) and extract the following fields. For each field, also compute a score "
#                 "(a percentage from 0 to 100) representing how closely the candidate's CV matches the corresponding value in the Position JSON.\n\n"
#                 "Rules:\n\n"
#                 "1. Only extract information from the provided CV text.\n"
#                 "2. If a field cannot be determined, output an empty list for list fields, or a zero value (and a score of 0) for numeric values.\n"
#                 "3. The final answer must be output strictly in JSON format, with keys corresponding exactly to the field names above.\n"
#                 "4. Use the following JSON structure for your output:\n"
#                 "{\n"
#                 "  \"candidateName\" : <str>\n"
#                 "  \"requiredSkills\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"niceToHave\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"languages\": {\n"
#                 "    \"value\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"certifications\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"responsibilities\": {\n"
#                 "    \"scraped\": [\n"
#                 "      ...\n"
#                 "    ],\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"minimumExperienceMonths\": {\n"
#                 "    \"value\": <number>,\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"level\": {\n"
#                 "    \"value\": \"<one of Intern, Junior, Mid, Senior, Lead>\",\n"
#                 "    \"score\": <number>\n"
#                 "  },\n"
#                 "  \"minimumEducationLevel\": {\n"
#                 "    \"value\": \"<one of HighSchool, Bachelor, Master, Doctorate>\",\n"
#                 "    \"score\": <number>\n"
#                 "  }\n"
#                 "}\n"
#             )
#         },
#         {
#             "role": "user",
#             "content": (
#                 f"A. CV :\n{cv_text}\n\n"
#                 f"B. Position :\n{position.json()}"
#             )
#         }
#     ]

# async def evaluate_bulk(cv_texts: List[str],position,max_workers: int = 3,token_limit: int = 10000,window_sec: int = 60) -> List[CVEvaluationResultDTO]:
    
#     sem = asyncio.Semaphore(max_workers)
#     cond = asyncio.Condition()   # lock + notification
#     window_start = time.monotonic()
#     tokens_consumed = 0

#     def sync_worker(cv_text: str) -> tuple[CVEvaluationResultDTO, int]:
#         client   = _client()
#         messages = _build_messages(cv_text, position)
#         completion = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=messages,
#             temperature=0.3,
#             max_completion_tokens=1024,
#             top_p=0.8,
#             stream=False,
#             response_format={"type": "json_object"},
#             seed=12345,
#         )

#         result_str = completion.choices[0].message.content
#         try:
#             dto = CVEvaluationResultDTO.model_validate_json(result_str)
#         except ValidationError as e:
#             raise Exception(f"Validation error parsing LLM output: {e}")

#         used = completion.usage.total_tokens
#         return dto, used

#     async def _worker(idx: int, text: str) -> CVEvaluationResultDTO:
#         nonlocal window_start, tokens_consumed

#         print(f"[{idx+1}] Task starting…")

#         # 1) Limită de concurență
#         async with sem:
#             # 2) Așteaptă la nevoie până la reset
#             while True:
#                 async with cond:
#                     elapsed = time.monotonic() - window_start
#                     if tokens_consumed < token_limit:
#                         # avem loc în fereastră
#                         break
#                     # altfel, calculează pauza rămasă
#                     to_wait = max(window_sec - elapsed, 0)
#                     print(f"[{idx+1}] Rate-limit atins: {tokens_consumed} tokens în {elapsed:.1f}s, aștept {to_wait:.1f}s")
#                 await asyncio.sleep(to_wait)
#                 # după pauză, resetează fereastra și anunță
#                 async with cond:
#                     window_start = time.monotonic()
#                     tokens_consumed = 0
#                     cond.notify_all()
#                     print(f"[{idx+1}] Fereastră resetată")

#             print(f"[{idx+1}/{len(cv_texts)}] Evaluating CV…")
#             dto, used = await anyio.to_thread.run_sync(sync_worker, text)
#             print(f"[{idx+1}] → {used} tokens for this CV")

#             # 3) Adaugă costul și, dacă iarăși treci pragul, declanșează reset
#             async with cond:
#                 tokens_consumed += used
#                 print(f"    Window total = {tokens_consumed} tokens")
#                 if tokens_consumed >= token_limit:
#                     elapsed = time.monotonic() - window_start
#                     to_wait = max(window_sec - elapsed, 0)
#                     print(f"[{idx+1}] Rate-limit atins după update: aștept {to_wait:.1f}s")
#                     # Ieși din lock ca să nu blochezi condiția
#                 else:
#                     # totul OK, nu resetăm acum
#                     return dto

#             # dacă am ajuns aici, înseamnă că tokens_consumed >= limit
#             await asyncio.sleep(to_wait)
#             async with cond:
#                 window_start = time.monotonic()
#                 tokens_consumed = 0
#                 cond.notify_all()
#                 print(f"[{idx+1}] Fereastră resetată după update")

#             return dto

#     tasks = [_worker(i, txt) for i, txt in enumerate(cv_texts)]
#     return await asyncio.gather(*tasks)




# async def evaluate_bulk(cv_texts: List[str],position,max_completion_tokens: int = 1024,window_sec: int = 60,token_limit: int = 15000) -> List[CVEvaluationResultDTO]:
#     """
#     Distribute work across multiple API keys, each with its own rate window.
#     """
#     api_keys = ["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","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"]

#     # 1) Build per-key state
#     key_queue = asyncio.Queue()
#     for key in api_keys:
#         key_queue.put_nowait(key)

#     per_key_state = {
#         key: {"window_start": time.monotonic(), "tokens": 0}
#         for key in api_keys
#     }

#     cond = asyncio.Condition()

#     def sync_worker(cv_text: str, api_key: str) -> tuple[CVEvaluationResultDTO, int]:
#         client = Groq(api_key=api_key)
#         messages = _build_messages(cv_text, position)
#         completion = client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=messages,
#             temperature=0.3,
#             max_completion_tokens=max_completion_tokens,
#             top_p=0.8,
#             stream=False,
#             response_format={"type": "json_object"},
#             seed=12345,
#         )

#         result_str = completion.choices[0].message.content
#         try:
#             dto = CVEvaluationResultDTO.model_validate_json(result_str)
#         except ValidationError as e:
#             dto = CVEvaluationResultDTO()
#             dto.candidateName = "Error parsing LLM"
#             print (f"Validation error parsing LLM output: {e}")

#         used = completion.usage.total_tokens
#         return dto, used

#     async def _worker(idx: int, text: str) -> CVEvaluationResultDTO:
#         print(f"[{idx+1}] Task pending…")

#         # grab a free key (blocks if all keys busy)
#         api_key = await key_queue.get()
#         state = per_key_state[api_key]

#         try:
#             # --- wait until this key has budget ---
#             while True:
#                 async with cond:
#                     now = time.monotonic()
#                     elapsed = now - state["window_start"]

#                     # roll window if expired
#                     if elapsed >= window_sec:
#                         state["window_start"] = now
#                         state["tokens"] = 0
#                         cond.notify_all()
#                         print(f"[{idx+1}] 🔄 Reset window for {api_key}")

#                     # check budget
#                     if state["tokens"] + max_completion_tokens <= token_limit:
#                         # reserve worst-case tokens
#                         state["tokens"] += max_completion_tokens
#                         break

#                     # otherwise, compute how long to wait
#                     to_wait = window_sec - elapsed
#                     print(f"[{idx+1}] ⏳ Key {api_key} exhausted ({state['tokens']} tokens), sleeping {to_wait:.1f}s")
#                 await asyncio.sleep(to_wait)

#             # --- do the work ---
#             attempt = 0
#             while True:
#                 attempt += 1
#                 try:
#                     print(f"[{idx+1}] ▶️ Using {api_key} to eval CV (attempt {attempt})…")
#                     dto, used = await anyio.to_thread.run_sync(sync_worker, text, api_key)
#                     print(f"[{idx+1}] ← {used} tokens used on {api_key}")
#                     break  # succesează, ieși din loop-ul de retry
#                 except RateLimitError:
#                     # dacă lovești rate-limit, așteaptă fix 10s și retry
#                     print(f"[{idx+1}] ⚠️ RateLimitError on {api_key}, retrying in 10s…")
#                     await asyncio.sleep(10)
#                 except Exception as e:
#                     # Dacă vrei să faci același back-off la orice eroare:
#                     print(f"[{idx+1}] ⚠️ Unexpected error: {e}, retrying in 10s…")
#                     await asyncio.sleep(10)

#             # --- adjust to real usage and release any extra reservation ---
#             async with cond:
#                 # we had reserved max_completion_tokens; correct to actual usage
#                 state["tokens"] -= (max_completion_tokens - used)
#                 print(f"    [{api_key}] Window now at {state['tokens']} tokens")
#                 cond.notify_all()

#             return dto

#         finally:
#             key_queue.put_nowait(api_key)

#     # fire off all CV evaluations in parallel
#     tasks = [_worker(i, txt) for i, txt in enumerate(cv_texts)]
#     return await asyncio.gather(*tasks, return_exceptions=False)


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
                "content": (
                    "You are an expert resume analyzer. Your task is to analyze the CV (A. given as plain text) "
                    "along with the Position (B. given as JSON) and extract the following fields. For each field, also compute a score "
                    "(a percentage from 0 to 100) representing how closely the candidate's CV matches the corresponding value in the Position JSON.\n\n"
                    "Rules:\n\n"
                    "1. Only extract information from the provided CV text.\n"
                    "2. If a field cannot be determined, output an empty list for list fields, or a zero value (and a score of 0) for numeric values.\n"
                    "3. The final answer must be output strictly in JSON format, with keys corresponding exactly to the field names above.\n"
                    "4. Use the following JSON structure for your output:\n"
                    "{\n"
                    "  \"candidateName\" : <str>\n"
                    "  \"requiredSkills\": {\n"
                    "    \"scraped\": [\n"
                    "      ...\n"
                    "    ],\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"niceToHave\": {\n"
                    "    \"scraped\": [\n"
                    "      ...\n"
                    "    ],\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"languages\": {\n"
                    "    \"value\": [\n"
                    "      ...\n"
                    "    ],\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"certifications\": {\n"
                    "    \"scraped\": [\n"
                    "      ...\n"
                    "    ],\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"responsibilities\": {\n"
                    "    \"scraped\": [\n"
                    "      ...\n"
                    "    ],\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"minimumExperienceMonths\": {\n"
                    "    \"value\": <number>,\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"level\": {\n"
                    "    \"value\": \"<one of Intern, Junior, Mid, Senior, Lead>\",\n"
                    "    \"score\": <number>\n"
                    "  },\n"
                    "  \"minimumEducationLevel\": {\n"
                    "    \"value\": \"<one of HighSchool, Bachelor, Master, Doctorate>\",\n"
                    "    \"score\": <number>\n"
                    "  }\n"
                    "}\n"
                )
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
            top_p=0.8,
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
                while True:
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
