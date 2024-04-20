import psycopg2

class LabSummary:
    def __init__(self, config):
        self.config = config

    def connect_db(self):
        try:
            self.connection = psycopg2.connect(**self.config)
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def fetch_lab_data(self, hadm_id, chart_date):
        self.connect_db()
        query = f"""
        SELECT d.category, d.label, l.charttime, l.value, l.valuenum, l.valueuom, l.ref_range_lower, l.ref_range_upper, l.flag
        FROM mimiciv_hosp.labevents AS l
        JOIN mimiciv_hosp.d_labitems AS d ON l.itemid = d.itemid
        WHERE l.hadm_id = %s AND DATE(l.charttime) = %s
        ORDER BY l.charttime DESC, d.category;
        """
        try:
            self.cursor.execute(query, (hadm_id, chart_date))
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching lab data: {e}")
            return []

    def get_available_dates(self, hadm_id):
        self.connect_db()
        query = f"""
        SELECT DISTINCT DATE(charttime)
        FROM mimiciv_hosp.labevents
        WHERE hadm_id = %s
        ORDER BY DATE(charttime);
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            dates = self.cursor.fetchall()
            return [date[0] for date in dates]
        except Exception as e:
            print(f"Error fetching available dates: {e}")
            return []
