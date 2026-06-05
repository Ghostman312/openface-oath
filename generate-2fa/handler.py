import pyotp, json, psycopg2, os, logging, secrets, base64

logging.basicConfig(level=logging.INFO)

def handle(req):
    try:
        payload = json.loads(req) if req else {}
        username = payload.get("username")

        if not username:
            return {"statusCode": 401, "body": "Username required."}

        key = base64.b32encode(secrets.token_bytes(20)).decode('utf-8')
        uri = pyotp.totp.TOTP(key).provisioning_uri(
            name=username,
            issuer_name=os.environ.get("ISSUER"))

        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PWD"),
            dbname=os.environ.get("DB_NAME")
        )

        cur = conn.cursor()

        cur.execute(
            """
            UPDATE users
            SET totp_key = %s
            WHERE username = %s;
            """,
            (key, username))
        
        conn.commit()
        cur.close()
        conn.close()

        return {
            "message": "TOTP created successfully.",
            "totp": uri
        }, 201

    except Exception as e:
        logging.error(f"Internal error : {str(e)}")
        return {
            "statut": "Error",
            "details": str(e)
        }, 500
