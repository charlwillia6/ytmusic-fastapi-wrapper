from database import create_db_and_tables

if __name__ == "__main__":
    print("Recreating database...")
    create_db_and_tables()
    print("Database recreated successfully!") 
