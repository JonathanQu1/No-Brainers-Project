"""Load quiz JSON, shuffle questions and choices, grade answers."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class PreparedQuestion:
    """One question with shuffled choices; correct_index is into shuffled list."""

    question: str
    choices: list[str]
    correct_index: int


def load_quiz(path: Path | str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "questions" not in data or not isinstance(data["questions"], list):
        raise ValueError("Quiz must contain a non-empty 'questions' list.")
    return data


def validate_quiz_file(path: Path | str) -> None:
    """Raise ``ValueError`` if the JSON is not a playable quiz (same rules as the app)."""
    data = load_quiz(path)
    questions = data["questions"]
    if not questions:
        raise ValueError("Quiz has no questions.")
    for i, raw in enumerate(questions):
        if not isinstance(raw, dict):
            raise ValueError(f"Question {i + 1} must be a JSON object.")
        try:
            q = {
                "question": raw.get("question", ""),
                "choices": list(raw.get("choices", [])),
                "correct_index": raw["correct_index"],
            }
            validate_question_dict(q)
        except KeyError as exc:
            raise ValueError(f"Question {i + 1}: missing field {exc.args[0]!r}.") from exc


def list_quiz_paths(data_dir: Path) -> list[Path]:
    """Return sorted paths to ``*.json`` quiz files in ``data_dir``."""
    if not data_dir.is_dir():
        return []
    return sorted(p for p in data_dir.glob("*.json") if p.is_file())


def read_quiz_title(path: Path) -> str:
    """Load only enough of a quiz file to show its title in a picker."""
    data = load_quiz(path)
    return str(data.get("title", path.stem))


def validate_question_dict(q: dict[str, Any]) -> None:
    text = str(q.get("question", "")).strip()
    if not text:
        raise ValueError("Each question needs non-empty question text.")
    choices = q.get("choices")
    if not isinstance(choices, list) or len(choices) < 2:
        raise ValueError("Each question needs at least two choices.")
    cleaned: list[str] = []
    for c in choices:
        s = str(c).strip()
        if not s:
            raise ValueError("Choices cannot be empty.")
        cleaned.append(s)
    ci = int(q["correct_index"])
    if not 0 <= ci < len(cleaned):
        raise ValueError("Correct answer must match one of the choices.")
    q["question"] = text
    q["choices"] = cleaned
    q["correct_index"] = ci


def save_quiz(path: Path | str, title: str, questions: list[dict[str, Any]]) -> None:
    """Write ``{title, questions}`` to JSON after validating each question."""
    if not questions:
        raise ValueError("Quiz must have at least one question.")
    out_questions: list[dict[str, Any]] = []
    for raw in questions:
        q = {
            "question": raw["question"],
            "choices": list(raw["choices"]),
            "correct_index": int(raw["correct_index"]),
        }
        validate_question_dict(q)
        out_questions.append(
            {"question": q["question"], "choices": q["choices"], "correct_index": q["correct_index"]}
        )
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"title": str(title).strip() or "Untitled quiz", "questions": out_questions}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def prepare_questions(raw_questions: list[dict[str, Any]]) -> list[PreparedQuestion]:
    """Shuffle question order; shuffle each question's choices while keeping correct answer."""
    items: list[PreparedQuestion] = []
    for q in raw_questions:
        text = q["question"]
        choices = list(q["choices"])
        orig_correct = int(q["correct_index"])
        if not 0 <= orig_correct < len(choices):
            raise ValueError(f"Invalid correct_index for question: {text!r}")
        correct_text = choices[orig_correct]
        random.shuffle(choices)
        new_correct = choices.index(correct_text)
        items.append(PreparedQuestion(question=text, choices=choices, correct_index=new_correct))
    random.shuffle(items)
    return items


def parse_choice_answer(raw: str, num_choices: int) -> int | None:
    """Return 0-based index if valid, else None."""
    raw = raw.strip()
    if not raw:
        return None
    try:
        n = int(raw)
    except ValueError:
        return None
    if 1 <= n <= num_choices:
        return n - 1
    return None
