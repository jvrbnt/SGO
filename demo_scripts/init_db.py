from backend.database import engine, Base, LocalSession
import backend.models as models

def reset_db():
    print("--- Droping and Creating Tables ---")
    # Borra todo lo anterior y crea la nueva estructura
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    reset_db()