#!/usr/bin/env python3
"""Bare-bones CLI geography quiz."""

from pathlib import Path

from quiz_engine import load_quiz, parse_choice_answer, prepare_questions


def main() -> None:
    root = Path(__file__).resolve().parent
    quiz_path = root / "data" / "geography_quiz.json"
    data = load_quiz(quiz_path)
    title = data.get("title", "Quiz")
    questions = prepare_questions(data["questions"])

    print(f"\n{title}\n{'-' * len(title)}")
    score = 0
    total = len(questions)

    for i, pq in enumerate(questions, start=1):
        print(f"\nQuestion {i}/{total}")
        print(pq.question)
        for j, choice in enumerate(pq.choices, start=1):
            print(f"  {j}. {choice}")

        while True:
            raw = input("Your answer (number): ")
            idx = parse_choice_answer(raw, len(pq.choices))
            if idx is not None:
                break
            print(f"Invalid input. Enter a number from 1 to {len(pq.choices)}.")

        if idx == pq.correct_index:
            score += 1
            print("Correct!")
        else:
            correct = pq.choices[pq.correct_index]
            print(f"Wrong. The correct answer was: {correct}")

    print(f"\n---\nFinal score: {score}/{total}")


if __name__ == "__main__":
    main()
