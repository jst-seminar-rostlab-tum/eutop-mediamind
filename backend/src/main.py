import os

import psycopg2
from dotenv import load_dotenv
from supabase import Client, create_client

# Load env variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Example code using psycopg2 (= adapter for Python)
# (See https://www.psycopg.org/docs/ for more info on how to use psycopg2)
try:
    # Connect to db
    connection = psycopg2.connect(DATABASE_URL, sslmode="require")
    print("Connection successful!")

    # Create a cursor to execute SQL queries
    cursor = connection.cursor()

    # Example query
    cursor.execute("SELECT NOW();")
    result = cursor.fetchone()
    print("Current Time:", result)

    # Close the cursor and connection
    cursor.close()
    connection.close()
    print("Connection closed.")

except Exception as e:
    print(f"Failed to connect: {e}")


# Example code using supabase-py SDK
# (See https://supabase.com/docs/reference/python on how to use supabase SDK)
try:
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized successfully!")

    # Example query: Fetch the current time from the database
    response = supabase.rpc("now").execute()
    if response.data:
        print("Current Time:", response.data)
    else:
        print("No data returned:", response.error)

except Exception as e:
    print(f"Failed to connect to Supabase: {e}")
