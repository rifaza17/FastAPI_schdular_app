import psycopg2, time

while True:
    try:
        conn = psycopg2.connect(
            host="arenberg.cpi08wga2nbk.us-west-2.rds.amazonaws.com",
            dbname="postgres",
            user="postgres",
            password="arenberg123",
            connect_timeout=5
        )
        conn.close()
    except Exception as e:
        print("Ping failed:", e)
    time.sleep(300)  # every 5 minutes
