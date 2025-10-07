from sqlalchemy import create_engine, text

db_host = "arenberg.cpi08wga2nbk.us-west-2.rds.amazonaws.com"
db_name = "stockdb"  # target db
db_user = "postgres"
db_password = "arenberg123"
db_port = 5432

# First connect to default database (postgres)
default_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/postgres"
engine = create_engine(default_url, isolation_level="AUTOCOMMIT")

try:
    with engine.connect() as conn:
        # Check if stockdb exists
        result = conn.execute(text("SELECT 1 FROM pg_database WHERE datname=:d"), {"d": db_name})
        exists = result.scalar()

        if exists:
            print(f"✅ Database '{db_name}' already exists.")
        else:
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"🎉 Database '{db_name}' created successfully.")

except Exception as e:
    print("❌ Error:", e)

stockdb_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
stock_engine = create_engine(stockdb_url)

with stock_engine.connect() as conn:
    print("✅ Connected to stockdb")
