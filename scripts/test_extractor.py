from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parents[1]


def main() -> None:
    sys.path.insert(0, str(ROOT_DIR / "apps" / "api" / "src"))
    from planproof_api.agent.extractor import extract_metadata  # noqa: E402

    if load_dotenv is not None:
        load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set.")

    context = "Need to call Bob about the Apollo project."
    metadata = extract_metadata(context)
    payload = metadata.model_dump()

    if "Bob" not in payload["ground_truth_entities"]:
        raise RuntimeError("Expected 'Bob' in ground_truth_entities.")
    if "Apollo" not in payload["ground_truth_entities"]:
        raise RuntimeError("Expected 'Apollo' in ground_truth_entities.")

    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
