import os
import json
import glob
from db import get_conn, upsert_node, insert_edge, fetch_graph_data
from parser import parse_file
from generator import calculate_layout, generate_xml

CONFIG_PATH = "config"
INPUT_DIR = "input"
OUTPUT_DIR = "output"

def load_json(filename):
    with open(os.path.join(CONFIG_PATH, filename), 'r') as f:
        return json.load(f)

def main():
    print("--- Starting C4 Merge System ---")
    
    # 1. Load Configs
    parse_cfg = load_json("parsing.json")
    style_cfg = load_json("styles.json")
    
    # 2. Connect DB
    conn = get_conn()
    
    # 3. Ingest Files
    files = glob.glob(os.path.join(INPUT_DIR, "*.drawio"))
    print(f"Found {len(files)} files to parse.")
    
    for fpath in files:
        print(f"Parsing {fpath}...")
        nodes, edges = parse_file(fpath, parse_cfg)
        
        for n in nodes:
            upsert_node(conn, n)
        for e in edges:
            insert_edge(conn, e['source'], e['target'], e['label'])
            
    print("Data merged into DB.")
    
    # 4. Fetch Unified Graph
    print("Fetching consolidated graph...")
    all_nodes, all_edges = fetch_graph_data(conn)
    
    if not all_nodes:
        print("No nodes found. Exiting.")
        return

    # 5. Layout Calculation
    print("Calculating layout...")
    layout_nodes = calculate_layout(all_nodes, all_edges)
    
    # 6. Generate Output
    out_file = os.path.join(OUTPUT_DIR, "consolidated_c4.drawio")
    generate_xml(layout_nodes, all_edges, style_cfg, out_file)
    
    print(f"Done! Result saved to: {out_file}")

if __name__ == "__main__":
    main()