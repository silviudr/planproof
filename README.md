# PlanProof — Productivity through Measurable Trust

PlanProof is a productivity planning API that treats trust as a measurable outcome, not a vibe.
It produces daily plans and grades them against deterministic rules so users can rely on the result.

## The Core Problem
Most AI productivity advice is untrustworthy because it is generated and judged by the same model.
The output can look confident while violating constraints, inventing details, or overlapping timeblocks.
This makes the plan feel helpful but fail in practice.

## The Solution: The Sandwich Architecture
PlanProof separates the pipeline into three explicit stages:
1) Extraction: Parse the user's context into constraints and keywords.
2) Generation: Produce a plan with explicit start and end times.
3) Deterministic Validation: Enforce constraints, check overlaps, and score recall in Python.

This architecture prevents a model from grading its own output.

## Key Technical Features
- Deterministic time math for overlap detection.
- Scheduled tasks must be in the future relative to the system's current date/time (the time box).
- Hallucination filters to prevent invented entities or times.
- Keyword recall metrics to ensure coverage of user-provided tasks.

## Example Messy Input
```text
okay so listen the honey do list for the next moon cycle or whatever we're calling the time it takes for the moon to look like a giant fingernail in the sky starts with the front door because the hinge is sighing like a Victorian orphan and i think we need to feed it some olive oil or maybe just a sacrifice of a single copper penny found under the car seat where the french fries go to die and then we really need to address the situation with the curtains because they're judging the way i eat cereal out of a tupperware lid at 4am so we should probably replace them with sheets of tinfoil or maybe just very large leaves if we can find a tree that's willing to donate its limbs to the cause of my privacy but also don't forget that the toaster has been smelling like burnt memories lately so we should probably shake it out over the balcony and see if any of our lost hopes fall out along with the crumbs of that sourdough bread we bought when we thought we were going to be the kind of people who make avocado toast every morning which was a lie we told ourselves during the great strawberry moon of last year and hey speaking of moons we need to reorganize the pantry so that all the circular foods are on the top shelf and the square foods are in the basement because the geometry of our snacks is currently clashing with the feng shui of my internal chaos and i can't have a square cracker in a round world right now honey it's just not sustainable for my mental ecosystem and then there's the matter of the bathroom mirror which keeps showing me a person i don't recognize who looks suspiciously like they need a nap and a haircut so we should probably drape a silk scarf over it and just guess where our eyebrows are for the next seventeen days while we focus on the real issue which is the fact that the wifi router is blinking in a rhythm that matches the theme song to that show about the bakeries in great britain and i think it's trying to tell me to buy more flour even though the oven is currently being used as a storage locker for all the sweaters i'm too emotionally attached to to wash so if you could just find a way to harness the static electricity from the cat's fur to charge my phone that would be great because i lost the charging cable in the Great Sofa Crevice of 2023 and i'm pretty sure it's joined a cult with the spare change and the remote control by now so the final task for the month is to build a shrine to the concept of "doing things later" out of empty seltzer cans and old receipts in the middle of the hallway so we have to parkour over it every time we want to go to bed which will improve our core strength and our ability to ignore the inevitable march of Tuesday.
```

## Observability with Opik
Each pipeline step is traced with Opik to measure:
- hard pass rate
- repair success rate
- entity accuracy
- confidence calibration

This makes the system debuggable and comparable across model variants.

## Tech Stack
- FastAPI
- Pydantic v2
- Opik
- OpenAI / Gemini (LLM backends)

## Local Setup
Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -e .
```

Run the API:
```bash
uvicorn planproof_api.main:app --host 0.0.0.0 --port 10000 --reload
```

The UI (static assets) is served at the root path.
