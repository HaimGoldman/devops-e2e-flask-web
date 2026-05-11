from flask import Flask, jsonify, request, redirect
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
        error_msg = str(e)

    balance = total_income - total_expenses
    balance_color = '#4CAF50' if balance >= 0 else '#f44336'

    rows_html = ''
    for t in transactions:
        sign = '+' if t['type'] == 'income' else '-'
        color = '#4CAF50' if t['type'] == 'income' else '#f44336'
        rows_html += f'''
        <tr>
          <td>{t["date"]}</td>
          <td>{t["category"]}</td>
          <td>{t["description"] or ""}</td>
          <td style="color:{color};font-weight:bold">{sign}₪{t["amount"]:.2f}</td>
          <td><form method="POST" action="/transactions/{t["id"]}/delete" style="margin:0">
            <button type="submit" style="background:none;border:none;cursor:pointer;color:#999;font-size:1.1em">✕</button>
          </form></td>
        </tr>'''

    html = f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>מנהל תקציב</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; background: #f0f2f5; padding: 0 16px; }}
    h1 {{ color: #333; }}
    .cards {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
    .card {{ flex: 1; min-width: 150px; background: white; border-radius: 8px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
    .card .label {{ color: #888; font-size: .85em; margin-bottom: 6px; }}
    .card .value {{ font-size: 1.8em; font-weight: bold; }}
    .form-card {{ background: white; border-radius: 8px; padding: 20px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.1); margin-bottom: 24px; }}
    .form-row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end; }}
    .form-row input, .form-row select {{ padding: 8px 10px; border: 1px solid #ddd; border-radius: 4px; font-size: .95em; }}
    .form-row input[name=amount] {{ width: 100px; }}
    .form-row input[name=category] {{ width: 120px; }}
    .form-row input[name=description] {{ flex: 1; min-width: 150px; }}
    .btn {{ background: #2196F3; color: white; border: none; padding: 9px 20px; border-radius: 4px; cursor: pointer; font-size: .95em; }}
    .btn:hover {{ background: #1976D2; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.1); }}
    th {{ background: #f5f5f5; text-align: right; padding: 10px 14px; font-size: .85em; color: #666; border-bottom: 1px solid #eee; }}
    td {{ padding: 10px 14px; border-bottom: 1px solid #f0f0f0; font-size: .9em; }}
    tr:last-child td {{ border-bottom: none; }}
    .error {{ color: red; padding: 12px; background: #fff3f3; border-radius: 4px; margin-bottom: 16px; }}
    .links {{ margin-top: 20px; font-size: .8em; color: #aaa; }}
    .links a {{ color: #aaa; margin-left: 12px; }}
  </style>
</head>
<body>
  <h1>מנהל תקציב ביתי</h1>
  {'<div class="error">שגיאת DB: ' + error_msg + '</div>' if error_msg else ''}
  <div class="cards">
    <div class="card">
      <div class="label">יתרה</div>
      <div class="value" style="color:{balance_color}">₪{balance:.2f}</div>
    </div>
    <div class="card">
      <div class="label">סה"כ הכנסות</div>
      <div class="value" style="color:#4CAF50">₪{total_income:.2f}</div>
    </div>
    <div class="card">
      <div class="label">סה"כ הוצאות</div>
      <div class="value" style="color:#f44336">₪{total_expenses:.2f}</div>
    </div>
  </div>

  <div class="form-card">
    <form method="POST" action="/transactions">
      <div class="form-row">
        <select name="type">
          <option value="expense">הוצאה</option>
          <option value="income">הכנסה</option>
        </select>
        <input name="amount" type="number" step="0.01" min="0.01" placeholder="סכום" required>
        <input name="category" type="text" placeholder="קטגוריה" required>
        <input name="description" type="text" placeholder="תיאור (אופציונלי)">
        <button type="submit" class="btn">הוסף</button>
      </div>
    </form>
  </div>

  <table>
    <thead>
      <tr><th>תאריך</th><th>קטגוריה</th><th>תיאור</th><th>סכום</th><th></th></tr>
    </thead>
    <tbody>
      {rows_html if rows_html else '<tr><td colspan="5" style="text-align:center;color:#aaa;padding:24px">אין עסקאות עדיין</td></tr>'}
    </tbody>
  </table>
  <div class="links"><a href="/stats">/stats</a><a href="/health">/health</a><a href="/metrics">/metrics</a></div>
</body>
</html>"""
    return html


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
