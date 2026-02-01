"""检查Neo4j数据库中的节点类型分布"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with driver.session() as session:
    # 查询所有节点类型及其数量
    result = session.run("""
        MATCH (n)
        RETURN labels(n)[0] AS label, count(n) AS count
        ORDER BY count DESC
    """)

    print("节点类型统计:")
    print("=" * 60)
    for record in result:
        print(f"{record['label']}: {record['count']} 个")

    print("\n" + "=" * 60)

    # 查询每种类型的一些示例
    result = session.run("""
        MATCH (n)
        WITH labels(n)[0] AS label, n
        ORDER BY label
        RETURN label, collect(id(n))[0..3] AS sample_ids
    """)

    print("\n各类型节点示例ID:")
    for record in result:
        print(f"{record['label']}: {record['sample_ids']}")

driver.close()
