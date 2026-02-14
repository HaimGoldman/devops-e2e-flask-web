from flask import Flask, jsonify
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'visitsdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'password'),
        port=os.getenv('DB_PORT', '5432')
    )
    return conn

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

@app.route('/')
def hello():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO visits (timestamp) VALUES (CURRENT_TIMESTAMP)')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error logging visit: {e}")
    
    return "Hello World!"

@app.route('/stats')
def stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM visits WHERE timestamp >= NOW() - INTERVAL '1 hour'")
        hour_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM visits WHERE timestamp >= NOW() - INTERVAL '1 day'")
        day_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM visits WHERE timestamp >= NOW() - INTERVAL '1 week'")
        week_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM visits WHERE timestamp >= NOW() - INTERVAL '1 month'")
        month_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        return jsonify({
            "last_hour": hour_count,
            "last_day": day_count,
            "last_week": week_count,
            "last_month": month_count
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "database": "disconnected", "error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)