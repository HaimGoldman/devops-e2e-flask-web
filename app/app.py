from flask import Flask, jsonify, request, redirect, render_template
import psycopg2
import os
import logging
from prometheus_flask_exporter import PrometheusMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
metrics = PrometheusMetrics(app)


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'visitsdb'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.environ['DB_PASSWORD'],
        port=os.getenv('DB_PORT', '5432')
    )
    return conn


def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                amount NUMERIC(10, 2) NOT NULL,
                category VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


@app.route('/')
def index():
    transactions = []
    total_income = 0
    total_expenses = 0
    error_msg = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, amount, category, description, type, date FROM transactions ORDER BY date DESC LIMIT 50')
        rows = cur.fetchall()
        for row in rows:
            transactions.append({
                'id': row[0], 'amount': float(row[1]), 'category': row[2],
                'description': row[3], 'type': row[4],
                'date': row[5].strftime('%Y-%m-%d %H:%M') if row[5] else ''
            })
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'income'")
        total_income = float(cur.fetchone()[0])
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'expense'")
        total_expenses = float(cur.fetchone()[0])
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to load transactions: {e}")
        error_msg = True

    balance = total_income - total_expenses
    balance_color = '#4CAF50' if balance >= 0 else '#f44336'

    return render_template('index.html',
        transactions=transactions,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        balance_color=balance_color,
        error_msg=error_msg
    )


@app.route('/transactions', methods=['POST'])
def add_transaction():
    try:
        amount = float(request.form['amount'])
        category = request.form['category'].strip()
        description = request.form.get('description', '').strip()
        tx_type = request.form['type']
        if tx_type not in ('income', 'expense'):
            return 'Invalid type', 400
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO transactions (amount, category, description, type) VALUES (%s, %s, %s, %s)',
            (amount, category, description or None, tx_type)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return str(e), 500
    from flask import redirect
    return redirect('/')


@app.route('/transactions/<int:tx_id>/delete', methods=['POST'])
def delete_transaction(tx_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('DELETE FROM transactions WHERE id = %s', (tx_id,))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        return str(e), 500
    from flask import redirect
    return redirect('/')


@app.route('/stats')
def stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'income'")
        total_income = float(cur.fetchone()[0])
        cur.execute("SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE type = 'expense'")
        total_expenses = float(cur.fetchone()[0])
        cur.close()
        conn.close()
        return jsonify({
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": total_income - total_expenses
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
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=8000)
