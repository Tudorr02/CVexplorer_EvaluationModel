from typing import List
from fastapi import FastAPI, HTTPException
from models import CvEvaluationRequest , BulkCvEvaluationRequest
from output_models import CVEvaluationResultDTO
from services import Evaluator
import os

env_var_names = ["GROQ_API_KEY_1","GROQ_API_KEY_2"]
API_KEYS = [os.getenv(name) for name in env_var_names if os.getenv(name)]

MODEL_NAME = "gemma2-9b-it"
MAX_COMPLETION_TOKENS = 1024

evaluator = Evaluator(
    api_keys=API_KEYS,
    model=MODEL_NAME,
    max_completion_tokens=MAX_COMPLETION_TOKENS,
)

app = FastAPI(title="Cv Analyzer API")

@app.post("/evaluate-cv",response_model=CVEvaluationResultDTO)
async def evaluate_cv(request: CvEvaluationRequest)-> CVEvaluationResultDTO:

    if not request.cv_text or not request.position:
        raise HTTPException(status_code=400, detail="Both cv_text and position must be provided.")
    
    result : CVEvaluationResultDTO = evaluator.evaluate(request.cv_text, request.position)

    return result

@app.post("/evaluate-cvs",response_model=List[CVEvaluationResultDTO])
async def evaluate_cvs(requests: BulkCvEvaluationRequest) -> List[CVEvaluationResultDTO]:
    if not requests.cvTexts or not requests.position:
        raise HTTPException(status_code=400, detail="Both cv_text and position must be provided.")

    results: List[CVEvaluationResultDTO] = await evaluator.evaluate_bulk(requests.cvTexts, requests.position)
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)




