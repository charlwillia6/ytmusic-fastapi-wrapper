from app.db.models import Base
from app.db.session import engine

def recreate_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    recreate_database() 
