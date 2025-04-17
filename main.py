from fastapi import FastAPI, HTTPException
from models import CvEvaluationRequest
from output_models import CVEvaluationResultDTO
from services import evaluate

app = FastAPI(title="Cv Analyzer API")

@app.post("/evaluate-cv",response_model=CVEvaluationResultDTO)
async def evaluate_cv(request: CvEvaluationRequest)-> CVEvaluationResultDTO:
    # Validate input
    print("ccccc")
    if not request.cv_text or not request.position:
        raise HTTPException(status_code=400, detail="Both cv_text and position must be provided.")
    
    # Call the Cv analysis function from services.py
    evaluation_result = evaluate(request.cv_text, request.position)
    return evaluation_result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
