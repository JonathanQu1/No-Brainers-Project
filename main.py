from backend.models import Users
from backend.database import Base, engine

Base.metadata.create_all(engine)

print("Database and tables created")