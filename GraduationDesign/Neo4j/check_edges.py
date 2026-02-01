"""检查边的连接情况"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with driver.session() as session:
    # 查看Network节点的连接情况
    result = session.run("""
        MATCH (n:Network)-[r]->(m)
        RETURN count(r) AS edge_count
    """)

    record = result.single()
    print(f"Network节点的出边数量: {record['edge_count']}")

    # 查看Network节点连接到什么类型的节点
    result = session.run("""
        MATCH (n:Network)-[r]->(m)
        RETURN labels(m)[0] AS target_type, count(r) AS count
        ORDER BY count DESC
        LIMIT 10
    """)

    print("\nNetwork节点连接的目标类型:")
    for record in result:
        print(f"  -> {record['target_type']}: {record['count']} 条")

    # 查看什么节点连接到Network
    result = session.run("""
        MATCH (n)-[r]->(m:Network)
        RETURN labels(n)[0] AS source_type, count(r) AS count
        ORDER BY count DESC
        LIMIT 10
    """)

    print("\n连接到Network节点的源类型:")
    for record in result:
        print(f"  {record['source_type']} -> : {record['count']} 条")

    # 随机选择几个Network节点查看其连接
    result = session.run("""
        MATCH (n:Network)-[r]-(m)
        WHERE id(n) IN [248, 249, 250]
        RETURN id(n) AS network_id, labels(m)[0] AS connected_type, id(m) AS connected_id, type(r) AS rel_type
        LIMIT 20
    """)

    print("\n前3个Network节点的连接示例:")
    for record in result:
        print(f"  Network[{record['network_id']}] --[{record['rel_type']}]--> {record['connected_type']}[{record['connected_id']}]")

driver.close()
