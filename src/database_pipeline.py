import os
import pandas as pd
import psycopg2  
from psycopg2.extras import RealDictCursor

def _get_db_connection():
    """
    PRIVATE HELPER: Opens a direct network socket to the live staging database.
    Dynamically pulls environment variables injected into the cloud environment.
    """
    try:
        return psycopg2.connect(
            host=os.getenv("SLEEPNAV_DB_HOST"),
            database=os.getenv("SLEEPNAV_DB_NAME"),
            user=os.getenv("SLEEPNAV_DB_USER"),
            password=os.getenv("SLEEPNAV_DB_PASSWORD"),
            port=os.getenv("SLEEPNAV_DB_PORT", 5432),
            connect_timeout=5
        )
    except Exception as e:
        print(f"📡 Database Connection Refused: {str(e)}")
        return None

# =====================================================================
# PIPELINE 1: SECURE PATIENT IDENTIFICATION & LOGISTICS EXTRACTION
# =====================================================================
def pipeline_verify_and_fetch_appointment(patient_name: str, dob: str) -> dict:
    """
    UNIVERSAL REAL-TIME ENTRYPOINT: Safely queries live corporate tables
    to retrieve records for ANY patient match dynamically.
    """
    clean_name = patient_name.strip().lower()
    clean_dob = dob.strip()
    
    # Parameterized SQL layout - protects network infrastructure from SQL injections
    query = """
        SELECT appointment_date, appointment_time, location_name, arrival_instructions
        FROM patient_appointments
        WHERE LOWER(patient_name) = %s AND date_of_birth = %s
        LIMIT 1;
    """
    
    try:
        conn = _get_db_connection()
        if conn is None:
            return {"error": "Staging database connection offline. Check environment variable secrets."}
            
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, (clean_name, clean_dob))
            record = cursor.fetchone()
            
        conn.close()
        return dict(record) if record else None

    except Exception as e:
        print(f"❌ Real-time Pipeline Fetch Error: {str(e)}")
        return {"error": f"Pipeline processing exception: {str(e)}"}

# =====================================================================
# PIPELINE 2: LIVE ADMINISTRATIVE TELEMETRY AGGREGATION
# =====================================================================
def pipeline_fetch_weekly_metrics() -> str:
    """
    Aggregates real-time row telemetry from live operational tables over 
    a rolling 7-day scale and structures it into an administrative payload.
    """
    query = """
        SELECT 
            c.clinic_name AS "Clinic_Name",
            COUNT(a.id) AS "Weekly_Patient_Volume",
            ROUND((COUNT(CASE WHEN a.status = 'cancelled' THEN 1 END) * 100.0 / COUNT(a.id)), 1) || '%' AS "Cancellation_Rate",
            ROUND((COUNT(CASE WHEN a.auth_status = 'missing' THEN 1 END) * 100.0 / COUNT(a.id)), 1) || '%' AS "Missing_Auth_Rate"
        FROM clinics c
        LEFT JOIN appointments a ON c.id = a.clinic_id
        WHERE a.scheduled_at >= NOW() - INTERVAL '7 days'
        GROUP BY c.clinic_name;
    """
    try:
        conn = _get_db_connection()
        if conn is None:
            # Informative fallback preview if cloud secrets are unconfigured during testing
            return "Error,Unable to stream data tables. Database host parameters are missing or unreachable."
            
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_csv(index=False)
        
    except Exception as e:
        print(f"❌ Live Aggregation Engine Fault: {str(e)}")
        return f"Error,Query telemetry execution failure: {str(e)}"