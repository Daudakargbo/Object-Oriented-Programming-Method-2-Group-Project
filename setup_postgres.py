import os
import subprocess
import time

import psycopg2
from dotenv import load_dotenv

load_dotenv()

hba_path = r"C:\Program Files\PostgreSQL\18\data\pg_hba.conf"
backup_path = hba_path + ".bak"
pg_ctl_path = r"C:\Program Files\PostgreSQL\18\bin\pg_ctl.exe"
data_dir = r"C:\Program Files\PostgreSQL\18\data"
postgres_password = os.getenv("POSTGRES_PASSWORD", "0000")


def reload_postgres():
    print("Reloading PostgreSQL configuration...")
    cmd = f'"{pg_ctl_path}" reload -D "{data_dir}"'
    subprocess.run(cmd, shell=True, check=True)
    time.sleep(2)

try:
    # 1. Backup pg_hba.conf if not already backed up
    if not os.path.exists(backup_path):
        with open(hba_path, "r") as f:
            original_content = f.read()
        with open(backup_path, "w") as f:
            f.write(original_content)
        print("Backup created at:", backup_path)
    else:
        with open(backup_path, "r") as f:
            original_content = f.read()
        print("Using existing backup at:", backup_path)

    # 2. Modify pg_hba.conf to use 'trust' for local connections
    # We replace scram-sha-256 with trust for local and IPv4/IPv6 loopbacks
    trust_content = original_content.replace(
        "127.0.0.1/32            scram-sha-256",
        "127.0.0.1/32            trust"
    ).replace(
        "::1/128                 scram-sha-256",
        "::1/128                 trust"
    )
    
    with open(hba_path, "w") as f:
        f.write(trust_content)
    print("Modified pg_hba.conf to 'trust' mode.")

    # 3. Reload config
    reload_postgres()

    # 4. Connect to postgres database without password (trust)
    print("Connecting to PostgreSQL...")
    # Try connecting via IPv4 localhost specifically to match the pg_hba rules
    conn = psycopg2.connect(host="127.0.0.1", user="postgres")
    conn.autocommit = True
    cur = conn.cursor()

    # 5. Set postgres user's password to the configured value
    print("Setting password for 'postgres' user...")
    cur.execute("ALTER USER postgres WITH PASSWORD %s;", (postgres_password,))

    # 6. Check and create the 'fitness_tracker' database
    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'fitness_tracker';")
    exists = cur.fetchone()
    if not exists:
        print("Creating database 'fitness_tracker'...")
        cur.execute("CREATE DATABASE fitness_tracker;")
    else:
        print("Database 'fitness_tracker' already exists.")

    cur.close()
    conn.close()
    print("Database configuration completed successfully.")

finally:
    # 7. Restore original pg_hba.conf
    if os.path.exists(backup_path):
        with open(backup_path, "r") as f:
            orig = f.read()
        with open(hba_path, "w") as f:
            f.write(orig)
        print("Restored original pg_hba.conf.")
        
        # 8. Reload to secure Postgres again
        reload_postgres()
        print("PostgreSQL configuration reloaded and secured.")
