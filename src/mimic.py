import psycopg2

# Database connection parameters
db_params = {
    'database': 'mimiciv',
    'user': 'postgres',
    'password': 'Mokpswd7!',
    'host': 'localhost',
    'port': '5432'
}

# Establish the database connection
conn = psycopg2.connect(**db_params)

# Create a cursor object
cur = conn.cursor()

# SQL query to count the number of patients
query = 'SELECT COUNT(*) FROM mimiciv_hosp.patients;'

try:
    # Execute the query
    cur.execute(query)
    
    # Fetch the result
    count = cur.fetchone()[0]
    
    print(f'Total number of patients: {count}')
    
except psycopg2.Error as e:
    print(f'An error occurred: {e}')
finally:
    # Close the cursor and the connection
    cur.close()
    conn.close()
