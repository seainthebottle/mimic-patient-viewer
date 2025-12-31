import psycopg2
import pandas as pd
from datetime import timedelta
from sqlalchemy import create_engine

class DataModel:
    def __init__(self, config = None):
        self.conn = None
        self.config = config
        self.engine = None
        self.cursor = None

    def connect_db(self, config = None):
        if config:
            self.config = config
        # ✅ SQLAlchemy 엔진 생성
        uri = f"postgresql+psycopg2://{self.config['user']}:{self.config['password']}@" \
                f"{self.config['host']}:{self.config['port']}/{self.config['dbname']}"
        self.engine = create_engine(uri)

        # ✅ psycopg2 connection 유지 (cursor 사용하는 함수 때문에)
        self.conn = psycopg2.connect(**self.config)
        self.cursor = self.conn.cursor()

        print("Database connection successful")

    def disconnect_db(self):
        if self.conn:
            self.conn.close()
        self.conn = None
        self.cursor = None
        self.engine = None
        self.config = None

    def fetch_lab_data(self, hadm_id, chart_date):
        if self.conn == None: return None
        #self.connect_db()
        query = f"""
        SELECT d.category, d.label, l.charttime, l.value, l.valuenum, l.valueuom, l.ref_range_lower, l.ref_range_upper, l.flag
        FROM mimiciv_hosp.labevents AS l
        JOIN mimiciv_hosp.d_labitems AS d ON l.itemid = d.itemid
        WHERE l.hadm_id = %s AND l.charttime::DATE = %s
        ORDER BY l.charttime DESC, d.category;
        """
        try:
            self.cursor.execute(query, (hadm_id, chart_date))
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error fetching lab data: {e}")
            return []
        #finally:
        #    self.disconnect_db()
    
    def get_admission_dates(self, hadm_id):
        if self.conn is None:
                return None, None
        return_value = []  # List of all dates from admission to discharge
        icu_dates = set()  # Set of ICU dates with "*" marker
        query_admission = f"""
            SELECT admittime::DATE, dischtime::DATE
            FROM mimiciv_hosp.admissions
            WHERE hadm_id = %s
        """
        query_icu = f"""
            SELECT intime::DATE, outtime::DATE
            FROM mimiciv_icu.icustays
            WHERE hadm_id = %s
        """
        try:
            # Fetch admission dates
            self.cursor.execute(query_admission, (hadm_id,))
            result = self.cursor.fetchone()
            if result:
                admission_date, discharge_date = result
                current_date = admission_date
                while current_date <= discharge_date:
                    return_value.append(current_date)
                    current_date += timedelta(days=1)

            # Fetch ICU intime and outtime ranges
            self.cursor.execute(query_icu, (hadm_id,))
            icu_stays = self.cursor.fetchall()
            for intime, outtime in icu_stays:
                current_date = intime
                while current_date <= outtime:
                    icu_dates.add(current_date)  # Add ICU dates to the set
                    current_date += timedelta(days=1)
        except Exception as e:
            print(f"Error fetching available dates: {e}")
        return return_value, icu_dates

    def fetch_input_data(self, hadm_id):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT starttime, endtime, amount, amountuom
        FROM mimiciv_icu.inputevents
        WHERE amountuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        #self.disconnect_db()
        return data
    
    def fetch_output_data(self, hadm_id):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT charttime, value, valueuom
        FROM mimiciv_icu.outputevents
        WHERE valueuom = 'ml' AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(hadm_id,))
        #self.disconnect_db()
        return data
    
    def fetch_event_data(self, hadm_id, item_id):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT charttime, valuenum
        FROM mimiciv_icu.chartevents
        WHERE itemid = %s AND hadm_id = %s
        """
        data = pd.read_sql_query(query, self.conn, params=(item_id, hadm_id,))
        #self.connect_db()
        return data
    
    def fetch_order_data(self, hadm_id, chart_date):
        if self.conn == None: return None
        #self.connect_db()
        cursor = self.conn.cursor()
        query = """
        SELECT p.poe_id, p.poe_seq, p.ordertime, p.order_type, p.order_subtype, p.order_status, d.field_value, ph.medication, ph.route, ph.frequency
        FROM mimiciv_hosp.poe p
        LEFT OUTER JOIN mimiciv_hosp.poe_detail d ON p.poe_id = d.poe_id
        LEFT OUTER JOIN mimiciv_hosp.pharmacy ph ON p.poe_id = ph.poe_id
        WHERE p.hadm_id = %s AND p.ordertime::DATE = %s AND (p.order_type <> 'Medications' OR ph.poe_id IS NOT NULL)
        ORDER BY p.ordertime ASC;
        """
        cursor.execute(query, (hadm_id, chart_date))
        rows = cursor.fetchall()
        cursor.close()
        #self.connect_db()
        return pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    
    def fetch_patient_info(self, hadm_id):
        if self.conn == None: return None
        #self.connect_db()
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
        #finally:
        #    self.disconnect_db()

    def fetch_diagnosis_data(self, hadm_id):
        #print(f"fetch_diagnosis_data: {hadm_id}")
        if self.conn == None: return None
        #self.connect_db()
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
        #finally:
        #    self.disconnect_db()

    def fetch_procedure_data(self, hadm_id):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT pr.seq_num, pr.icd_version, pr.icd_code, dicd.long_title, pr.chartdate
        FROM mimiciv_hosp.procedures_icd pr
        JOIN mimiciv_hosp.d_icd_procedures dicd 
          ON pr.icd_code = dicd.icd_code AND pr.icd_version = dicd.icd_version
        WHERE pr.hadm_id = %s
        ORDER BY pr.chartdate, pr.seq_num
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=['sequential_number', 'icd_version', 'icd_code', 'procedure_name', 'procedure_date'])
        except Exception as e:
            print(f"Error fetching procedure data: {e}")
            return pd.DataFrame()
        #finally:
        #    self.disconnect_db()

    def fetch_emar_data(self, hadm_id, chart_date):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT 
            e.subject_id AS subject_id,
            e.hadm_id AS hadm_id,
            e.emar_id AS emar_id,
            e.emar_seq AS emar_seq,
            e.poe_id AS poe_id,
            e.pharmacy_id AS pharmacy_id,
            e.charttime AS charttime,
            e.medication AS medication,
            e.event_txt AS event_txt,
            e.scheduletime AS scheduletime,
            e.storetime AS storetime,
            STRING_AGG(DISTINCT d.administration_type, ',') AS administration_type,
            SUM(CASE WHEN d.dose_due ~ '^[0-9]+(\.[0-9]+)?$' THEN CAST(d.dose_due AS NUMERIC) ELSE 0 END) AS dose_due,
            STRING_AGG(DISTINCT d.dose_due_unit, ',') AS dose_due_unit,
            SUM(CASE WHEN d.dose_given ~ '^[0-9]+(\.[0-9]+)?$' THEN CAST(d.dose_given AS NUMERIC) ELSE 0 END) AS dose_given,
            STRING_AGG(DISTINCT d.dose_given_unit, ',') AS dose_given_unit,
            STRING_AGG(DISTINCT d.route, ',') AS route
        FROM mimiciv_hosp.emar e
        LEFT JOIN mimiciv_hosp.emar_detail d ON e.emar_id = d.emar_id AND e.emar_seq = d.emar_seq
        WHERE e.hadm_id = %s AND e.charttime::DATE = %s 
        GROUP BY e.hadm_id, e.emar_id, e.emar_seq, e.poe_id, e.pharmacy_id, e.charttime, e.medication, e.event_txt, e.scheduletime, e.storetime
        ORDER BY e.charttime;
        """
        try:
            self.cursor.execute(query, (hadm_id, chart_date,))
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=[
                'subject_id', 'hadm_id', 'emar_id', 'emar_seq', 'poe_id', 'pharmacy_id', 
                'charttime', 'medication', 'event_txt', 
                'scheduletime', 'storetime', 'administration_type', 'dose_due', 
                'dose_due_unit', 'dose_given', 'dose_given_unit', 'route'
            ])
        except Exception as e:
            print(f"Error fetching eMAR data: {e}")
            return pd.DataFrame()
        #finally:
        #    self.disconnect_db()

    def fetch_discharge_notes(self, hadm_id):
        if self.conn == None: return None
        #self.connect_db()
        query = """
        SELECT note_id, subject_id, note_type, note_seq, charttime, storetime, text
        FROM mimiciv_note.discharge
        WHERE hadm_id = %s
        ORDER BY note_seq;
        """
        try:
            self.cursor.execute(query, (hadm_id,))
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, columns=['note_id', 'subject_id', 'note_type', 'note_seq', 'charttime', 'storetime', 'text'])
        except Exception as e:
            print(f"Error fetching discharge notes: {e}")
            return pd.DataFrame()
        #finally:
        #    self.disconnect_db()

    def fetch_admission_list(self, condition):
        if self.conn == None: return pd.DataFrame() # 연결 없으면 빈 DF 반환
        #self.connect_db()

        condition_str = ""
        if condition['expire'] == True:
            condition_str += " AND a.hospital_expire_flag = 1"
        if condition['admission_days_low_limit'] > 0:
            condition_str += f" AND (EXTRACT(EPOCH FROM (a.dischtime - a.admittime)) / 86400.0) >= {condition['admission_days_low_limit']}"
        if condition['icustay_days_low_limit'] > 0:
            condition_str += f"""
                AND a.hadm_id IN (
                    SELECT hadm_id
                    FROM mimiciv_icu.icustays
                    GROUP BY hadm_id
                    HAVING SUM(EXTRACT(EPOCH FROM (outtime - intime)) / 86400.0) >= {condition['icustay_days_low_limit']}
                )
            """

        query = f"""
        SELECT 
            a.hadm_id, 
            a.subject_id,
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
        WHERE TRUE {condition_str}
        GROUP BY a.hadm_id, a.subject_id, p.gender, p.anchor_age, p.anchor_year, a.admittime, a.dischtime, a.deathtime
        ORDER BY a.hadm_id;
        """
        try:
            self.cursor.execute(query, ())
            rows = self.cursor.fetchall()
            return pd.DataFrame(rows, 
                columns=['hadm_id', 'subject_id', 'gender', 'age_at_admission', 'died_in_hospital', 'admittime', 'dischtime', 'icu_intime', 'icu_outtime'])
        except Exception as e:
            print(f"Error fetching discharge notes: {e}")
            return pd.DataFrame({'Error': [str(e)]})
        #finally:
        #    self.disconnect_db()
