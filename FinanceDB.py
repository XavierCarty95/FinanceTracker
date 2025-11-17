import  os
from  dotenv import load_dotenv
import psycopg2

load_dotenv()

class FinanceDB:
    def __init__(self):
        db_url = os.getenv('DB_URL')
        if not db_url:
            raise Exception('DB_URL not set')
        self.conn = psycopg2.connect(db_url)
        self.cur = self.conn.cursor()
    def execute(self, query, params=None):
        self.cur.execute(query, params or ())
        self.conn.commit()
    def fetchone(self):
        return self.cur.fetchone()
    def fetchall(self):
        return self.cur.fetchall()
    def rollback(self):
        self.conn.rollback()
    def close(self):
        self.cur.close()
        self.conn.close()