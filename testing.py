from backend.models import Users
from backend.database import Base, engine
from backend.auth_service import signup, login


Base.metadata.create_all(bind=engine)

print("Signup 1")
success, message = signup("John","1234")
print(success,message)

print("Signup 2")
success,message = signup("Jack","1234")
print(success, message)

print("Login 1")
success, message, Users = login("John", "1234")
print(success,message)

print("login 2")
success, message, Users = login("Jack", "1234")
print(success, message)

print("Login 3")
sucess, message, Users = login("Jill","Hello")
print(success, message)