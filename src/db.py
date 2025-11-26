import psycopg2
import json
import os

def get_conn():
    return psycopg2.connect(
        host="db",
        database=os.environ.get("POSTGRES_DB"),
        user=os.environ.get("POSTGRES_USER"),
        password=os.environ.get("POSTGRES_PASSWORD")
    )

def upsert_node(conn, node):
    sql = """
    INSERT INTO c4_nodes (id, name, c4_type, description, meta_data)
    VALUES (%s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        description = EXCLUDED.description,
        meta_data = EXCLUDED.meta_data;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (node['id'], node['name'], node['type'], node['description'], json.dumps(node)))
    conn.commit()

def insert_edge(conn, source, target, label):
    sql = """
    INSERT INTO c4_edges (source_id, target_id, label)
    VALUES (%s, %s, %s)
    ON CONFLICT (source_id, target_id) DO UPDATE SET
        label = EXCLUDED.label;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (source, target, label))
    conn.commit()

def fetch_graph_data(conn):
    nodes = []
    edges = []
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, c4_type, description FROM c4_nodes")
        for row in cur.fetchall():
            nodes.append({"id": row[0], "name": row[1], "type": row[2], "description": row[3]})
        
        cur.execute("SELECT source_id, target_id, label FROM c4_edges")
        for row in cur.fetchall():
            edges.append({"source": row[0], "target": row[1], "label": row[2]})
    return nodes, edges