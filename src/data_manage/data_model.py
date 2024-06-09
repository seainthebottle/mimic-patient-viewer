import psycopg2
import pandas as pd

class DataModel:
    def __init__(self, config):
        self.config = config

    def connect_db(self):
        try:
            self.conn = psycopg2.connect(**self.config)
            self.cursor = self.conn.cursor()
            print("Database connection successful")
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def disconnect_db(self):
        self.conn.close()

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
        finally:
            self.disconnect_db()


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
        finally:
            self.disconnect_db()

    def fetch_input_data(self, hadm_id):
        self.conn = psycopg2.connect(**self.config)
        query = """
        SELECT starttime, endtime, amount, amountuom
        FROM mimiciv_icu.inputevents
        WHERE amountuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        self.conn.close()
        return data
    

    def fetch_output_data(self, hadm_id):
        self.conn = psycopg2.connect(**self.config)
        query = """
        SELECT charttime, value, valueuom
        FROM mimiciv_icu.outputevents
        WHERE valueuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        self.conn.close()
        return data
    

    def fetch_event_data(self, hadm_id, item_id):
        self.conn = psycopg2.connect(**self.config)
        query = """
        SELECT charttime, valuenum
        FROM mimiciv_icu.chartevents
        WHERE itemid = %s AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(item_id, hadm_id,))
        self.conn.close()
        return data
    

    def fetch_order_data(self, hadm_id, chart_date):
        conn = psycopg2.connect(**self.config)
        cursor = conn.cursor()
        query = """
        SELECT p.poe_id, p.poe_seq, p.ordertime, p.order_type, p.order_subtype, p.order_status, d.field_value, ph.medication, ph.route, ph.frequency
        FROM mimiciv_hosp.poe p
        LEFT OUTER JOIN mimiciv_hosp.poe_detail d ON p.poe_id = d.poe_id
        LEFT OUTER JOIN mimiciv_hosp.pharmacy ph ON p.poe_id = ph.poe_id
        WHERE p.hadm_id = %s AND DATE(p.ordertime) = %s AND (p.order_type <> 'Medications' OR ph.poe_id IS NOT NULL)
        ORDER BY p.ordertime ASC;
        """
        cursor.execute(query, (hadm_id, chart_date))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    
    def fetch_patient_info(self, hadm_id):
        self.connect_db()
        query = """
        SELECT 
            p.gender,
            p.anchor_age + (EXTRACT(YEAR FROM a.admittime) - p.anchor_year) AS age_at_admission,
            a.deathtime IS NOT NULL AS died_in_hospital,
            a.admittime,
            a.dischtime,
            MIN(icu.intime) AS icu_intime,
            MAX(icu.outtime) AS icu_outtime
        FROM mimiciv_hosp.admissions a
        JOIN mimiciv_hosp.patients p ON a.subject_id = p.subject_id
        LEFT JOIN mimiciv_icu.icustays icu ON a.hadm_id = icu.hadm_id
        WHERE a.hadm_id = %s
        GROUP BY p.gender, p.anchor_age, p.anchor_year, a.admittime, a.dischtime, a.deathtime;
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            result = self.cursor.fetchone()
            if result:
                return {
                    "gender": result[0],
                    "age_at_admission": result[1],
                    "died_in_hospital": result[2],
                    "admittime": result[3],
                    "dischtime": result[4],
                    "icu_intime": result[5],
                    "icu_outtime": result[6]
                }
            else:
                return {}
        except Exception as e:
            print(f"Error fetching patient info: {e}")
            return {}
        finally:
            self.disconnect_db()

    def fetch_diagnosis_data(self, hadm_id):
        #print(f"fetch_diagnosis_data: {hadm_id}")
        self.connect_db()
        query = """
        SELECT di.seq_num, di.icd_version, di.icd_code, dicd.long_title
        FROM mimiciv_hosp.diagnoses_icd di
        JOIN mimiciv_hosp.d_icd_diagnoses dicd 
          ON di.icd_code = dicd.icd_code AND di.icd_version = dicd.icd_version
        WHERE di.hadm_id = %s
        ORDER BY di.seq_num
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=['sequential_number', 'icd_version', 'icd_code', 'diagnosis_description'])
        except Exception as e:
            print(f"Error fetching diagnosis data: {e}")
            return pd.DataFrame()
        finally:
            self.disconnect_db()


    def fetch_procedure_data(self, hadm_id):
        self.connect_db()
        query = """
        SELECT pr.seq_num, pr.icd_version, pr.icd_code, dicd.long_title, pr.chartdate
        FROM mimiciv_hosp.procedures_icd pr
        JOIN mimiciv_hosp.d_icd_procedures dicd 
          ON pr.icd_code = dicd.icd_code AND pr.icd_version = dicd.icd_version
        WHERE pr.hadm_id = %s
        ORDER BY pr.chartdate
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=['sequential_number', 'icd_version', 'icd_code', 'procedure_name', 'procedure_date'])
        except Exception as e:
            print(f"Error fetching procedure data: {e}")
            return pd.DataFrame()
        finally:
            self.disconnect_db()