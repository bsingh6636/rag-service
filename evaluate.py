import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

from annotated_types.test_cases import cases
import httpx

from app.rag import NO_ANSWER
from app.schemas import RagAnswer

ROOT: Path = Path(__file__).resolve().parent

parser = argparse.ArgumentParser(description="Evaluate the RAG API")
parser.add_argument(
    "--cases",
    default="eval/cases.json",
    help="Case-file path relative to the project root"
)
args = parser.parse_args()
cases_path = ROOT / args.cases
cases = json.loads(cases_path.read_text(encoding="utf-8"))


timestamp: str = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
output : Path = ROOT / "eval" / f"results-{cases_path.stem}-{timestamp}.json"

print("Cases:", cases_path)
print("Questions:", len(cases))


def observe(payload: dict) -> str:
    answer = RagAnswer.model_validate(payload)

    if answer.answer == NO_ANSWER and not answer.sources:
        return "refuse"

    if answer.sources and answer.answer.strip() and answer.answer != NO_ANSWER:
        return "answer"

    return "invalid"


results = []

with httpx.Client(base_url="http://127.0.0.1:8000", timeout=90) as client:
    for case in cases:
        started = perf_counter()
        result = {
            **case,
            "answer_correct": None,
            "citations_supported": None,
        }

        try:
            response = client.post("/ask", json={"question": case["question"]})
            result["http_status"] = response.status_code
            result["response"] = response.json()
            result["observed_behavior"] = (
                observe(result["response"])
                if response.status_code == 200
                else "http_error"
            )
        except (httpx.HTTPError, ValueError) as exc:
            result["observed_behavior"] = "error"
            result["error"] = type(exc).__name__

        result["elapsed_ms"] = round((perf_counter() - started) * 1000)
        result["behavior_match"] = (
            result["observed_behavior"] == case["expected_behavior"]
        )
        results.append(result)
        output.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(
            case["id"],
            result["observed_behavior"],
            result["elapsed_ms"],
            "ms",
            flush=True,
        )

matched = sum(result["behavior_match"] for result in results)
print(f"Expected answer/refusal behavior matched: {matched}/{len(results)}")
print("Saved:", output)