from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 10

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """
You are a deterministic character-level string transformer.

Task:
- Read the input as individual characters.
- Output the exact same characters in reverse order.
- Do not group characters into words, tokens, or subwords.
- Do not drop, add, replace, or move any character incorrectly.
- Silently verify that the output contains the same number of characters as the input.
- Return only the reversed string, with no explanation, no quotes, and no extra text.

Examples:
- background -> dnuorgkcab
- assignment -> tnemngissa
- statushttp -> ptthsutats
- httpstatusapi -> ipasutatsptth
- webhook -> koohbew
- httpcode -> edocptth
"""

USER_PROMPT = """
Input: httpstatus
Output:
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt up to NUM_RUNS_TIMES and return True if any output matches EXPECTED_OUTPUT.

    Prints "SUCCESS" when a match is found.
    """
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 0},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            return True
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    return False

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)
