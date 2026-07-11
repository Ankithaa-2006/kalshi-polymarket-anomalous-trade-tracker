import sqlite3
con = sqlite3.connect('prediction_market_tracker.db')
tables = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
for t in tables:
    print(t[0])
con.close()
