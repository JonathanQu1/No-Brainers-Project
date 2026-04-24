import csv
import os


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