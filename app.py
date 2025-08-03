from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import datetime
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64

app = Flask(__name__)

# MySQL Connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="kamali@1606#",
    database="rainharvest_db"
)
cursor = db.cursor()

@app.route('/')
def index():
    cursor.execute("SELECT tank_level FROM tank_data ORDER BY date DESC LIMIT 1")
    result = cursor.fetchone()
    predicted_level = round(result[0] * 1.10, 2) if result else None
    today = datetime.date.today().strftime('%B %d, %Y')
    return render_template("index.html", date=today, prediction=predicted_level)

@app.route('/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        date = datetime.date.today()
        rainfall = float(request.form['rainfall'])
        inflow = float(request.form['inflow'])
        usage = float(request.form['usage'])
        tank_level = float(request.form['tank_level'])
        cursor.execute(
            "INSERT INTO tank_data (date, rainfall, inflow, `usage`, tank_level) VALUES (%s, %s, %s, %s, %s)",
            (date, rainfall, inflow, usage, tank_level)
        )
        db.commit()
        return redirect(url_for('index'))
    return render_template("log.html")

@app.route('/dashboard')
def dashboard():
    cursor.execute("SELECT date, rainfall, inflow, `usage`, tank_level FROM tank_data ORDER BY date")
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=["date", "rainfall", "inflow", "usage", "tank_level"])
    df["date"] = pd.to_datetime(df["date"])

    # Predictions
    if not df.empty:
        latest = df.iloc[-1]
        usage_today = latest["usage"]
        tank_level_latest = latest["tank_level"]
        predicted_rainfall = df["rainfall"].tail(3).mean().round(2) if len(df) >= 3 else df["rainfall"].mean().round(2)
    else:
        usage_today = 0
        tank_level_latest = 0
        predicted_rainfall = 0

    records = df.to_dict(orient='records')

    return render_template(
        "dashboard.html",
        records=records,
        tank_level=int(tank_level_latest),
        predicted_rainfall=predicted_rainfall,
        usage_today=int(usage_today),
        avg_savings=32
    )

if __name__ == '__main__':
    app.run(debug=True)
