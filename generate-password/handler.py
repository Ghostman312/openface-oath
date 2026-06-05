import bcrypt, string, secrets, json, psycopg2, os, logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

def handle(req):
    # Generate password and salt
    pwd_not_valid = True
    while pwd_not_valid:
        pwd = ''.join(secrets.choice(string.ascii_letters+string.digits+string.punctuation) for i in range(24))
        pwd_not_valid = (any(c.islower() for c in pwd) and
                        any(c.isupper() for c in pwd) and
                        any(c.isdigit() for c in pwd) and
                        any(c in string.punctuation for c in pwd))
    
    # Encrypt password
    hash = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

    # Store password into Postgres database
    try:
        payload = json.loads(req) if req else {}
        username = payload.get("username")

        if not username:
            return {"statusCode": 400, "body": "Username required."}

        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PWD"),
            dbname=os.environ.get("DB_NAME")
        )

        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS users;")

        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            totp_key TEXT,
            password_expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        cur.execute(
            """
            INSERT INTO users (username, password_hash, password_expires_at) 
            VALUES (%s, %s, %s)
            ON CONFLICT (username) 
            DO UPDATE SET 
                password_hash = EXCLUDED.password_hash,
                created_at = CURRENT_TIMESTAMP;
            """,
            (username, hash.decode('utf-8'), datetime.now() + timedelta(days=180)))
        
        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "User created successfully.",
            "password": pwd
        }, 201

    except Exception as e:
        logging.error(f"Internal error : {str(e)}")
        return {
            "statut": "Error",
            "details": str(e)
        }, 500
