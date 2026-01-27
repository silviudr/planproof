import requests
import time

URL = "http://localhost:10000/api/plan"
# scenarios = [
#     ("Meeting at 1 PM, buy milk, leave at 5 PM", "Should Pass"),
#     ("Meeting at 1 PM, meeting at 1 PM, laundry", "Should Fail (Overlap)"),
#     ("I need to go to the gym, buy eggs, and call Bob", "Should Pass"),
#     ("Meeting at 5 AM, buy coffee", "Should Fail (Expired)"),
#     ("Busy until 10 AM, meeting at 9 AM, write report", "Should Fail (Start-Gate)"),
#     ("Leave by 3 PM, deep work from 2 PM to 5 PM", "Should Fail (Deadline)"),
#     ("Call Sarah about Apollo at 2 PM, buy groceries", "Should Pass"),
#     ("Lunch at 12 PM for 1 hour, project sync at 12:30 PM", "Should Fail (Overlap)"),
#     ("Meeting at 3:15 PM, another meeting at 4:15 PM, buy milk", "Should Pass"),
#     ("Write report, review Q4 plan, respond to emails", "Should Pass"),
#     ("Meet Mike at 2 PM, meet John at 2:05 PM", "Should Fail (Overlap)"),
#     ("Dentist appointment at 8 AM, buy toothpaste", "Should Pass"),
#     ("Gym at 5 AM, pick up breakfast", "Should Fail (Expired)"),
#     ("Meeting at 1 PM, meeting at 2 PM, buy milk", "Should Pass"),
#     ("Travel to airport at 4 PM, flight at 4:30 PM", "Should Pass"),
#     ("Prepare taxes by 5 PM, work block from 4 PM to 6 PM", "Should Fail (Deadline)"),
#     ("Workshop at 9 AM for 2 hours, deep work at 10 AM", "Should Fail (Overlap)"),
#     ("Doctor appointment at 3 PM, pick up meds at 3:45 PM", "Should Pass"),
#     ("Standup at 10 AM, standup at 10 AM", "Should Fail (Overlap)"),
#     ("Meeting at 1 PM, buy milk, wash car", "Should Fail (Hallucination)"),
# ]

# for i, (text, expectation) in enumerate(scenarios):
#     print(f"Running Scenario {i+1}: {expectation}")
#     variant = "v1_naive" if i % 2 == 0 else "v3_agentic_repair"
#     print(f"Prompt: {text}")
#     print(f"Variant: {variant}")
#     response = requests.post(URL, json={
#         "context": text,
#         "current_time": "2026-01-25T11:00:00Z",
#         "timezone": "America/New_York",
#         "variant": variant
#     })
#     if response.ok:
#         payload = response.json()
#         print(
#             "Result: "
#             f"status={payload.get('validation', {}).get('status')}, "
#             f"repairs={payload.get('debug', {}).get('repair_attempted')}, "
#             f"success={payload.get('debug', {}).get('repair_success')}"
#         )
#         print(f"Errors: {payload.get('validation', {}).get('errors')}")
#         print(f"Metrics: {payload.get('validation', {}).get('metrics')}")
#     else:
#         print(f"Result: HTTP {response.status_code} {response.text}")
#     print("============================")
#     time.sleep(1)

comparison_scenarios = [
    (
        "Meeting at 1 PM, meeting at 1 PM, buy milk",
        "v1_naive",
        "Expected fail (overlap; no repair)",
    ),
    (
        "Meeting at 1 PM, meeting at 1 PM, buy milk",
        "v3_agentic_repair",
        "Expected pass after repair (overlap resolved)",
    ),
    (
        "Busy until 10 AM, meeting at 9 AM, write report",
        "v1_naive",
        "Expected fail (start-gate; no repair)",
    ),
    (
        "Busy until 10 AM, meeting at 9 AM, write report",
        "v3_agentic_repair",
        "Expected pass after repair (shifted to >=10 AM)",
    ),
    (
        "Leave by 5 PM, deep work from 4 PM to 6 PM",
        "v1_naive",
        "Expected fail (deadline; no repair)",
    ),
    (
        "Leave by 5 PM, deep work from 4 PM to 6 PM",
        "v3_agentic_repair",
        "Expected pass after repair (end time adjusted)",
    ),
]

for i, (text, variant, expectation) in enumerate(comparison_scenarios):
    print(f"Running Comparison {i+1} ({variant}): {expectation}")
    print(f"Prompt: {text}")
    print(f"Variant: {variant}")
    response = requests.post(URL, json={
        "context": text,
        "current_time": "2026-01-25T11:00:00Z",
        "timezone": "America/New_York",
        "variant": variant,
    })
    if response.ok:
        payload = response.json()
        print(
            "Result: "
            f"status={payload.get('validation', {}).get('status')}, "
            f"repairs={payload.get('debug', {}).get('repair_attempted')}, "
            f"success={payload.get('debug', {}).get('repair_success')}"
        )
        print(f"Errors: {payload.get('validation', {}).get('errors')}")
        print(f"Metrics: {payload.get('validation', {}).get('metrics')}")
        print("----------------------------")
    else:
        print(f"Result: HTTP {response.status_code} {response.text}")
    print("============================")
    time.sleep(1)
