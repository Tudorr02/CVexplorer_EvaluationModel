# CVexplorer_EvaluationModel

## Description
This repository contains the **document evaluation service** for the **CVexplorer** platform. The service uses a **Large Language Model (LLM)** hosted on **Groq Cloud** ( the **Gemma-2 9b-it model**) to evaluate candidate CVs against job positions. For each analyzed field (skills, experience, education, certifications, languages, etc..), the LLM returns a **similarity score** along with the **corresponding extracted data** from the CV. This enables a structured, detailed, and automated evaluation of candidates, both individually and in bulk.


## Technologies Used
- **FastAPI** – for exposing the evaluation API
- **Groq Cloud** – LLM hosting and querying
- **Gemma-2 9b-it** – LLM used for semantic evaluation
- **Uvicorn** – ASGI server used to run the FastAPI app
- **Pydantic** – for request/response models and validation
- **AnyIO** – concurrency layer for async tasks

## Configuration
### 1. Environment Variables

The service requires one or more **Groq Cloud API keys** set via environment variables:

- `GROQ_API_KEY_1`, `GROQ_API_KEY_2`, ...

You can define multiple API keys to enable **key rotation ** when querying the LLM.

Example on Windows (Powershell):
```bash
$env:GROQ_API_KEY_1="your_first_key"
$env:GROQ_API_KEY_2="your_second_key"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
### 3. Run the FastAPI Server

```bash
python main.py
```

## Features

- Evaluate a single CV against a job position and return a structured evaluation.
- Bulk evaluation for multiple CVs concurrently.
- Rate limiting management and token tracking per Groq API key.
- Load balancing across multiple API keys to prevent throttling.
- Custom prompt engineering to instruct the LLM to return evaluations in a predefined JSON schema.

## API Endpoints

### ```POST /evaluate-cv```
> Evaluate a single CV against a position.

#### Request Body ( example )

```
{
  "cv_text": "Full CV text here",
  "position": {
    "name": "Data Scientist",
    "requiredSkills": ["Python", "Machine Learning"],
    "niceToHave": ["Docker", "Kubernetes"],
    "languages": ["English"],
    "certifications": ["AWS Certified"],
    "responsibilities": [],
    "minimumExperienceMonths": 24,
    "level": "mid",
    "minimumEducationLevel": "bachelor"
  }
}
```

### ```POST /evaluate-cvs```
> Evaluate multiple CVs in bulk against a position

#### Request Body ( example )

```
{
  "cvTexts": ["CV text 1", "CV text 2", "..."],
  "position": { ... same as above ... }
}
```

#### Sample Response ( example )
Example response returned by either of the endpoints:
```
{
  "candidateName": "John Doe",
  "requiredSkills": {
    "scraped": ["Python", "Machine Learning"],
    "score": 90.0
  },
  "niceToHave": {
    "scraped": ["Docker"],
    "score": 50.0
  },
  "languages": {
    "value": ["English"],
    "score": 100.0
  },
  "certifications": {
    "scraped": ["AWS Certified"],
    "score": 100.0
  },
  "responsibilities": {
    "scraped": ["Develop ML models"],
    "score": 80.0
  },
  "minimumExperienceMonths": {
    "value": 30,
    "score": 100.0
  },
  "level": {
    "value": "Senior",
    "score": 100.0
  },
  "minimumEducationLevel": {
    "value": "Master",
    "score": 100.0
  }
}

```

## See also :

- **Backend Repo**: [CVexplorer - Backend](https://github.com/Tudorr02/CVexplorer_Backend)
- **Frontend Repo**: [CVexplorer - Frontend](https://github.com/Tudorr02/CVexplorer_Frontend)

