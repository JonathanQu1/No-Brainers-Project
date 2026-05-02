import csv
import os


REQUIRED_COLUMNS = {"question", "answer"}


def load_questions():
    questions = []

    file_path = os.path.join("data", "questions.csv")

    with open(file_path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            questions.append({
                "question": row["question"],
                "answer": row["answer"].strip().lower() == "true"
            })

    return questions


def parse_questions_csv(file_path):
    """Opens a quiz CSV file, check that it's valid, and return its questions.

    Each question is returned as {"question": str, "answer": bool}.
    If anything is wrong with the file (missing columns, empty fields,
    bad answer values, etc.), this function raises a ValueError that
    explains which row caused the problem.
    """
    questions = []

    with open(file_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is empty.")

        headers = {(c or "").strip().lower() for c in reader.fieldnames}
        missing = REQUIRED_COLUMNS - headers
        if missing:
            raise ValueError(
                f"CSV is missing required column(s): {', '.join(sorted(missing))}."
            )

        for line_no, row in enumerate(reader, start=2):
            question = (row.get("question") or "").strip()
            answer_raw = (row.get("answer") or "").strip().lower()

            if not question:
                raise ValueError(f"Row {line_no}: 'question' is empty.")
            if answer_raw not in {"true", "false"}:
                raise ValueError(
                    f"Row {line_no}: 'answer' must be True or False "
                    f"(got '{row.get('answer')}')."
                )

            questions.append(
                {"question": question, "answer": answer_raw == "true"}
            )

    if not questions:
        raise ValueError("CSV contains no question rows.")

    return questions