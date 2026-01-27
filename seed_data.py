# seed_data.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from faker import Faker
import time

# Setup
engine = create_engine('sqlite:///production.db')
Session = sessionmaker(bind=engine)
session = Session()
fake = Faker()

def generate_bulk_data(n=100300):
    print(f"Generating {n} users... this might take a minute.")
    users = []
    start_time = time.time()
    
    for _ in range(n):
        users.append(User(
            full_name=fake.name(),
            email=fake.unique.email(),
            bio=fake.text()
        ))
        
        # Batch insert every 10,000 to save memory
        if len(users) >= 10000:
            session.bulk_save_objects(users)
            session.commit()
            users = []
            print(f"Saved batch...")

    # Save remaining
    if users:
        session.bulk_save_objects(users)
        session.commit()
    
    print(f"Finished in {time.time() - start_time:.3f} seconds.")

if __name__ == "__main__":
    generate_bulk_data()