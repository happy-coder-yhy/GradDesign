"""检查Network节点的坐标情况"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with driver.session() as session:
    # 查询Network节点的坐标情况
    result = session.run("""
        MATCH (n:Network)
        RETURN
            count(n) AS total,
            count(n.x) AS has_x,
            count(n.y) AS has_y
    """)

    record = result.single()
    print("Network节点坐标统计:")
    print(f"总数: {record['total']}")
    print(f"有x坐标: {record['has_x']}")
    print(f"有y坐标: {record['has_y']}")

    # 查看几个Network节点的示例
    print("\n" + "=" * 60)
    result = session.run("""
        MATCH (n:Network)
        RETURN id(n) AS id, n.x AS x, n.y AS y
        LIMIT 5
    """)

    print("\n前5个Network节点的坐标:")
    for record in result:
        print(f"ID: {record['id']}, x: {record['x']}, y: {record['y']}")

driver.close()
