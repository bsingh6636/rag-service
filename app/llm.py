import json 

import httpx

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

def ask_direct( question : str ) -> DirectAnswer :
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

    if not isinstance(data  ,dict) or data.get("stop_reason" ) != "end_turn" : 
        raise ValueError ( "Model response did not finish normally" )

    text = "".join(
        block["text"]
        for block in data.get("context" , [] )
        if isinstance ( block , dict ) and block.get("type") == "text"
    )

    return DirectAnswer.model_validate_json(text)