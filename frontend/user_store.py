import csv
import os
import hashlib
from datetime import datetime

USERS_FILE = os.path.join("data", "users.csv")
SCORES_FILE = os.path.join("data", "scores.csv")


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