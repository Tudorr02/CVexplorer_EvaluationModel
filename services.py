from typing import Dict, Any
from models import PositionDTO
from groq import Groq  # Ensure you have this package installed
from output_models import CVEvaluationResultDTO
from pydantic import ValidationError
def evaluate(cv_text: str, position: PositionDTO) -> Dict[str, Any]:
    client = Groq(api_key="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")
    # Construct the messages for the chat completion request.
    messages = [
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

    # Create the chat completion by calling the Groq API
    completion = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=messages,
        temperature=0.3,
        max_completion_tokens=1024,
        top_p=0.8,
        stream=False,
        response_format={"type": "json_object"},
        stop=None,
        seed=12345,
    )

    # Assuming the returned structure contains the analysis in completion.choices[0].message
    result_str = completion.choices[0].message.content
     # Validate and parse the JSON output using the ResumeAnalysisResult model
    try:
        analysis_result = CVEvaluationResultDTO.model_validate_json(result_str)
    except ValidationError as e:
        raise Exception(f"Validation error: {e}")

    return analysis_result
