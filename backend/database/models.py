import psycopg2
import json

DATABASE_URL = "postgresql://postgres.qmjzxwgpowsfudonfjzw:bajarleyoNA37!@aws-1-us-west-2.pooler.supabase.com:6543/postgres"


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def create_table():
    """Crea la tabla jobs si no existe."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            company TEXT,
            location TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            modality TEXT,
            summary TEXT,
            url TEXT,
            score INTEGER,
            score_breakdown JSONB,
            query TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def save_jobs(jobs: list[dict], query: str):
    """Guarda lista de ofertas. Ignora duplicados por ID."""
    conn = get_connection()
    cur = conn.cursor()

    for job in jobs:
        cur.execute("""
            INSERT INTO jobs (
                id, source, title, company, location,
                salary_min, salary_max, modality, summary,
                url, score, score_breakdown, query
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO UPDATE SET
                score = EXCLUDED.score,
                score_breakdown = EXCLUDED.score_breakdown;
        """, (
            job.get("id"),
            job.get("source"),
            job.get("title"),
            job.get("company"),
            job.get("location"),
            job.get("salary", {}).get("min"),
            job.get("salary", {}).get("max"),
            job.get("modality"),
            job.get("summary"),
            job.get("url"),
            job.get("score"),
            json.dumps(job.get("score_breakdown", {})),
            query,
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"[DB] {len(jobs)} ofertas guardadas")


def get_all_jobs() -> list[dict]:
    """Retorna todas las ofertas guardadas."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM jobs ORDER BY score DESC;")
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(cols, row)) for row in rows]