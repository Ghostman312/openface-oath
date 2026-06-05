import pyotp, json, psycopg2, os, logging, bcrypt

logging.basicConfig(level=logging.INFO)

def handle(req):
    try:
        payload = json.loads(req) if req else {}
        username = payload.get("username")
        password = payload.get("password")
        totp_code = payload.get("totp_code")

        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PWD"),
            dbname=os.environ.get("DB_NAME")
        )

        cur = conn.cursor()

        cur.execute("SELECT password_hash, totp_key FROM users WHERE username = %s;", (username,))
        fetched_user = cur.fetchone()

        if fetched_user is None:
            return { "authenticated": False, "message": "Invalid username." }, 401

        password_hash = fetched_user[0]
        totp_key = fetched_user[1]


        if not bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return { "authenticated": False, "message": "Password required." }, 401


        if totp_key is not None:
            if totp_code is None:
                return { "authenticated": False, "message": "TOTP code required." }, 401
                    
        if not pyotp.TOTP(totp_key).verify(totp_code):
            return { "authenticated": False, "message": "Invalid TOTP code." }, 401

        return { "authenticated": True }, 200

    except Exception as e:
        logging.error(f"Internal error : {str(e)}")
        return {
            "statut": "Error",
            "details": str(e)
        }, 500
