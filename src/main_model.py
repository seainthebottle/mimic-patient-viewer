import psycopg2

class MainModel:
    def __init__(self, dbname, user, password, host='localhost', port=5432):
        self.dbname = dbname
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = None

    def connect(self):
        """Connect to the PostgreSQL database server."""
        try:
            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port
            )
            print('Connection successful.')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            if self.conn is not None:
                self.conn.close()
                print('Database connection closed.')
    
    def fetch_admissions(self):
        """Query data from the mimiciv_hosp.admissions table."""
        try:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM mimiciv_hosp.admissions'
            cursor.execute(query)
            # fetch all the rows
            records = cursor.fetchall()
            cursor.close()
            return records
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
        
    def fetch_admission(self, hadm_id):
        """Query data from the mimiciv_hosp.admissions table."""
        try:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM mimiciv_hosp.admissions WHERE hadm_id = %s'
            cursor.execute(query, (hadm_id,))
            # fetch all the rows
            record = cursor.fetchone()
            cursor.close()
            return record
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
            return None
    
    def close(self):
        """Close the database connection."""
        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')
