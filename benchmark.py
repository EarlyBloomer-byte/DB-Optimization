# benchmark.py
from sqlalchemy import create_engine, text
import time

engine = create_engine('sqlite:///production.db')

def run_query_test():
    # Pick a name you know exists or just a random string pattern
    # The database has to scan ALL 100k rows to find this because there is no index.
    search_term = "Michael%" 
    query = text("SELECT * FROM users WHERE full_name LIKE :name")
    
    start = time.time()
    with engine.connect() as conn:
        result = conn.execute(query, {"name": search_term}).fetchall()
    end = time.time()
    
    print(f"Found {len(result)} records.")
    print(f"Query Time (No Index): {end - start:.5f} seconds")

if __name__ == "__main__":
    run_query_test()