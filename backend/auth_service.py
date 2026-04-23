from backend.database import SessionLocal
from backend.models import Users


def signup(username, password):
    session = SessionLocal()

    try:
        username = username.strip()
        password = password.strip()

        if not username or not password:
            return False, "Username and Password cannot be empty"
        
        existing_user = session.query(Users).filter_by(username=username).first()
        if existing_user:
            return False, "Username already exists"

        new_user = Users(username=username, password=password)
        session.add(new_user)
        session.commit()

        return True, "Signup Successful"

    except Exception as e:
        session.rollback()
        return False, f"Signup Failed: {e}"
    finally:
        session.close()

def login(username, password):
    session = SessionLocal()
    try:
        username = username.strip()
        password = password.strip()

        if not username and not password:
            return False, "Username and password cant be empty", None
        user = session.query(Users).filter_by(username=username).first()
        if not user:
            return False, "Username does not exist", None
        if user.password != password:
            return False, "Incorrect password", None
        return True,"Login Successful.", user
    except Exception as e:
        return False, f"Login Failed: {e}", None
    finally:
        session.close()


