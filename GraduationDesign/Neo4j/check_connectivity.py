"""检查节点类型的连通性"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with driver.session() as session:
    # 检查各类型节点的连通性
    node_types = ['StandPoint', 'RunwayPoint', 'AircraftRoad', 'Network']

    for node_type in node_types:
        result = session.run(f"""
            MATCH (n:{node_type})-[r]->()
            RETURN count(r) AS out_edges
        """)
        out_count = result.single()['out_edges']

        result = session.run(f"""
            MATCH ()-[r]->(n:{node_type})
            RETURN count(r) AS in_edges
        """)
        in_count = result.single()['in_edges']

        print(f"{node_type}: 出边={out_count}, 入边={in_count}")

    # 找一个有双向连通性的示例
    print("\n" + "=" * 60)
    print("尝试找StandPoint之间的路径:")

    result = session.run("""
        MATCH (a:StandPoint), (b:StandPoint)
        WHERE id(a) < id(b)
        WITH a, b, sqrt((a.x - b.x)^2 + (a.y - b.y)^2) AS dist
        WHERE dist > 100 AND dist < 1000
        ORDER BY dist DESC
        RETURN id(a) AS id1, a.x AS x1, a.y AS y1, id(b) AS id2, b.x AS x2, b.y AS y2, dist
        LIMIT 1
    """)

    record = result.single()
    if record:
        print(f"\n找到两个StandPoint节点:")
        print(f"  起点: id={record['id1']}, x={record['x1']}, y={record['y1']}")
        print(f"  终点: id={record['id2']}, x={record['x2']}, y={record['y2']}")
        print(f"  距离: {record['dist']:.2f}米")

        # 尝试找路径
        result = session.run("""
            MATCH path = shortestPath((a)-[*..10]-(b))
            WHERE id(a) = $id1 AND id(b) = $id2
            RETURN length(path) AS path_length,
                   [node in nodes(path) | labels(node)[0]] AS node_types
        """, id1=record['id1'], id2=record['id2'])

        record = result.single()
        if record and record['path_length'] > 0:
            print(f"\n找到路径！长度: {record['path_length']} 跳")
            print(f"节点类型序列: {record['node_types']}")

driver.close()
