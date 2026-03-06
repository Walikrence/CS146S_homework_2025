import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 10

# TODO: Fill this in!
YOUR_SYSTEM_PROMPT = """You reverse the order of letters in a word. Output only the final reversed word, nothing else.

How to reverse:
1. Split the word into a sequence of letters, left to right (e.g. "cat" → c, a, t).
2. Reversing means: the first letter becomes the last, the last becomes the first; the second becomes the second-to-last, and so on. In other words, take the letters from the end of the word to the beginning, in that order.
3. Do not change or skip any letter—repeated letters stay repeated, only their positions are reversed (e.g. "status" has two t's and two s's; reversed is "sutats").
4. Write the reversed letters in order to form the output word. The result must have the same length as the input (every letter is moved, none added or dropped).
5. Your reply must be exactly one word: the reversed string. No spaces, no newlines, no explanation, no punctuation.

Examples (split into letters, then reverse):
- Word: cat → letters: c, a, t → reversed: tac
- Word: http → letters: h, t, t, p → reversed: ptth
- Word: status → letters: s, t, a, t, u, s → reversed: sutats
- Word: httpstatus → letters: h, t, t, p, s, t, a, t, u, s → reversed: sutatsptth
- Word: hello → letters: h, e, l, l, o → reversed: olleh
- Word: world → letters: w, o, r, l, d → reversed: dlrow
- Word: python → letters: p, y, t, h, o, n → reversed: nohtyp
- Word: abc → letters: a, b, c → reversed: cba
- Word: programming → letters: p, r, o, g, r, a, m, m, i, n, g → reversed: gnimmargorp
- Word: username → letters: u, s, e, r, n, a, m, e → reversed: emanresu
- Word: webpage → letters: w, e, b, p, a, g, e → reversed: egapbew
- Word: testing → letters: t, e, s, t, i, n, g → reversed: gnitset
- Word: address → letters: a, d, d, r, e, s, s → reversed: sserdda
- Word: successful → letters: s, u, c, c, e, s, s, f, u, l → reversed: lufsseccus
- Word: development → letters: d, e, v, e, l, o, p, m, e, n, t → reversed: tnempoleved

Common mistake: reversing only part of the word or swapping segments gives wrong length or wrong order. Always reverse the entire string as one sequence (first letter → last position, last letter → first position)."""

USER_PROMPT = """
Reverse the order of letters in the following word. Only output the reversed word, no other text:

httpstatus
"""


EXPECTED_OUTPUT = "sutatsptth"

def test_your_prompt(system_prompt: str) -> bool:
    """Run the prompt NUM_RUNS_TIMES and return True only if all runs match EXPECTED_OUTPUT.

    Does not exit early on success; completes all rounds for stability validation.
    """
    success_count = 0
    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        response = chat(
            model="mistral-nemo:12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": USER_PROMPT},
            ],
            options={"temperature": 1, "num_ctx": 8192},
        )
        output_text = response.message.content.strip()
        if output_text.strip() == EXPECTED_OUTPUT.strip():
            print("SUCCESS")
            success_count += 1
        else:
            print(f"Expected output: {EXPECTED_OUTPUT}")
            print(f"Actual output: {output_text}")
    print(f"Result: {success_count}/{NUM_RUNS_TIMES} passed")
    return success_count == NUM_RUNS_TIMES

if __name__ == "__main__":
    test_your_prompt(YOUR_SYSTEM_PROMPT)   