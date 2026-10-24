import json 

import httpx

import logging
from time import perf_counter

from pydantic import ValidationError

from app.config import settings
from app.schemas import DirectAnswer 

SYSTEM = (
    "Answer briefly from your own knowledge. State assumptions explicitly. "
    "Return ONLY one JSON object, without Markdown fences or extra text. "
    "Confidence is your self-assessment from 0 to 1. "
    "Use an empty assumptions list when none are needed. "
    "Match this JSON schema: "
    + json.dumps(DirectAnswer.model_json_schema())
)

logger = logging.getLogger(__name__)

def ask_direct( question : str ) -> DirectAnswer :
    started = perf_counter()
    logger.info("MWAPI request started model = %s" , settings.chat_model)
    response = httpx.post(
        settings.mwapi_url.rstrip("/") + "/messages",
        headers = {
            "x-api-key" : settings.mwapi_api_key,
            "anthropic-version" : "2023-06-01",
        },
        json = {
            "model" : settings.chat_model ,
            "max_tokens" : 512 ,
            "system" : SYSTEM, 
            "messages" : [
                { "role" : "user" , "content"  : question}
            ],
        },
        timeout = 45
    )

    response.raise_for_status()
    data = response.json()

    logger.info(
        "MWAPI response status=%s elapsed_ms=%.0f",
        response.status_code,
        response,
        (perf_counter() - started) * 1000,
    )

    body_for_log = json.dumps(data, indent=2, ensure_ascii=False)

    if settings.mwapi_api_key:
        body_for_log = body_for_log.replace(
            settings.mwapi_api_key, "[REDACTED]"
        )

    logger.info("MWAPI response JSON:\n%s", body_for_log)

 

    if not isinstance(data, dict):
        logger.error("MWAPI response has an unexpected envelope type")
        raise ValueError("Unexpected response format")

    logger.info("MWAPI stop_reason=%s", data.get("stop_reason"))

    if data.get("stop_reason") != "end_turn":
        raise ValueError("Model response did not finish normally")


    text = "".join(
        block["text"]
        for block in data.get("content" , [] )
        if isinstance ( block , dict ) and block.get("type") == "text"
    )

    logger.info("Model text extracted chars=%d", len(text))

    try : 
        answer = DirectAnswer.model_validate_json(text)
    except ValidationError as exc :
        logger.error(
            "Model valdation failed : %s",
            exc.errors(
                include_input = False ,
                include_context = False ,
                include_url = False
            ),
        )
        raise

    logger.info("Model answer validated")
    return answer