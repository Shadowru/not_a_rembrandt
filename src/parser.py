import hashlib
import xml.etree.ElementTree as ET
import json

def generate_semantic_id(c4_name, c4_type):
    raw = f"{c4_name}:{c4_type}".lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()

def parse_file(filepath, config):
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    nodes = {} # internal_id -> semantic_data
    parsed_nodes = []
    parsed_edges = []

    # 1. Parse Nodes
    for obj in root.findall(f".//{config['object_tag']}"):
        c4_name = obj.get(config['attributes']['name'])
        c4_type = obj.get(config['attributes']['type'])
        
        if not c4_name or not c4_type:
            continue
            
        if c4_type in config.get('ignored_types', []):
            continue

        desc = obj.get(config['attributes']['description'], "")
        internal_id = obj.get('id')
        semantic_id = generate_semantic_id(c4_name, c4_type)
        
        node_data = {
            "id": semantic_id,
            "name": c4_name,
            "type": c4_type,
            "description": desc
        }
        nodes[internal_id] = node_data
        parsed_nodes.append(node_data)

    # 2. Parse Edges (mxCells that are edges)
    for cell in root.findall(".//mxCell[@edge='1']"):
        src = cell.get('source')
        tgt = cell.get('target')
        val = cell.get('value', '')
        
        # Check if source and target are known C4 objects
        if src in nodes and tgt in nodes:
            parsed_edges.append({
                "source": nodes[src]['id'],
                "target": nodes[tgt]['id'],
                "label": val
            })
            
    return parsed_nodes, parsed_edges