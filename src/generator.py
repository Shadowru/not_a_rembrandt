import networkx as nx
import json
from jinja2 import Environment, FileSystemLoader

def calculate_layout(nodes, edges):
    # Создаем граф для расчетов
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n['id'])
    for e in edges:
        G.add_edge(e['source'], e['target'])
    
    # Используем spring layout (силовой алгоритм)
    # scale=800 растягивает граф, чтобы элементы не слипались
    pos = nx.spring_layout(G, k=2, iterations=50, scale=800, seed=42)
    
    layout_nodes = []
    
    # Смещаем координаты, чтобы они начинались с положительных значений (напр. 100, 100)
    min_x = min(p[0] for p in pos.values())
    min_y = min(p[1] for p in pos.values())
    
    for node in nodes:
        x, y = pos[node['id']]
        # Нормализация + отступ
        final_x = int((x - min_x) + 100)
        final_y = int((y - min_y) + 100)
        
        layout_nodes.append({
            **node,
            "x": final_x,
            "y": final_y
        })
        
    return layout_nodes

def generate_xml(nodes, edges, styles_config, output_path):
    # Подготовка данных для шаблона
    # Маппинг типа C4 на стиль и цвет
    processed_nodes = []
    for n in nodes:
        c_type = n['type']
        # Fallback to 'System' if type not found
        color = styles_config['colors'].get(c_type, "#999999")
        base_style = styles_config['shapes'].get(c_type, styles_config['shapes']['System'])
        
        # Собираем полный стиль
        full_style = f"{base_style}fillColor={color};strokeColor=#FFFFFF;fontColor=#FFFFFF;"
        
        n['style'] = full_style
        n['w'] = styles_config['default_width']
        n['h'] = styles_config['default_height']
        processed_nodes.append(n)

    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template('diagram.xml.j2')
    
    xml_content = template.render(nodes=processed_nodes, edges=edges)
    
    with open(output_path, "w") as f:
        f.write(xml_content)