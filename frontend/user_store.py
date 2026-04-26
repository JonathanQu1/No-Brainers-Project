import csv
import os
import hashlib
from datetime import datetime

USERS_FILE = os.path.join("data", "users.csv")
SCORES_FILE = os.path.join("data", "scores.csv")
FLASHCARDS_FILE = os.path.join("data", "flashcards.csv")


def make_data_files():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password_hash"])

    if not os.path.exists(SCORES_FILE):
        with open(SCORES_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "score", "total", "date"])

    if not os.path.exists(FLASHCARDS_FILE):
        with open(FLASHCARDS_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "set_name", "term", "definition", "date"])


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def user_exists(username):
    make_data_files()

    with open(USERS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return True

    return False


def signup_user(username, password):
    make_data_files()

    if user_exists(username):
        return False

    with open(USERS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([username, hash_password(password)])

    return True


def verify_user(username, password):
    make_data_files()
    password_hash = hash_password(password)

    with open(USERS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["password_hash"] == password_hash:
                return True

    return False


def save_score(username, score, total):
    make_data_files()

    with open(SCORES_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([username, score, total, datetime.now().strftime("%Y-%m-%d %H:%M")])


def get_last_score(username):
    make_data_files()
    last_score = None

    with open(SCORES_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                last_score = row

    return last_score


def get_attempt_count(username):
    make_data_files()
    count = 0

    with open(SCORES_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                count += 1

    return count


def save_flashcard(username, set_name, term, definition):
    make_data_files()

    with open(FLASHCARDS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [username, set_name, term, definition, datetime.now().strftime("%Y-%m-%d %H:%M")]
        )


def get_set_names(username):
    make_data_files()
    seen = set()
    set_names = []

    with open(FLASHCARDS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                set_name = (row["set_name"] or "").strip()
                if set_name and set_name not in seen:
                    seen.add(set_name)
                    set_names.append(set_name)

    return set_names


def get_set_flashcards(username, set_name):
    make_data_files()
    cards = []

    with open(FLASHCARDS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username and row["set_name"] == set_name:
                term = row.get("term", row.get("front", ""))
                definition = row.get("definition", row.get("back", ""))
                cards.append({"term": term, "definition": definition})

    return cards


def delete_set(username, set_name):
    make_data_files()

    kept_rows = []
    with open(FLASHCARDS_FILE, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames or [
            "username",
            "set_name",
            "term",
            "definition",
            "date",
        ]
        for row in reader:
            if not (row["username"] == username and row["set_name"] == set_name):
                kept_rows.append(row)

    with open(FLASHCARDS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(kept_rows)