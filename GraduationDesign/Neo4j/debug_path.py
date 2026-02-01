"""调试路径查找"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

with driver.session() as session:
    # 检查节点248和627的连接
    start_id = 248
    goal_id = 627

    # 查看节点的连接情况
    result = session.run("""
        MATCH (n)-[r]->(m)
        WHERE id(n) IN [$start_id, $goal_id]
        RETURN id(n) AS from_id, id(m) AS to_id, labels(m)[0] AS to_type, type(r) AS rel_type
        LIMIT 10
    """, start_id=start_id, goal_id=goal_id)

    print(f"节点 {start_id} 和 {goal_id} 的出边连接:")
    for record in result:
        print(f"  {record['from_id']} --[{record['rel_type']}]--> {record['to_type']}[{record['to_id']}]")

    # 尝试找一条路径
    result = session.run("""
        MATCH path = shortestPath((a {id: $start_id})-[*..10]-(b {id: $goal_id}))
        RETURN length(path) AS path_length, [node in nodes(path) | id(node)] AS node_ids
        LIMIT 1
    """, start_id=start_id, goal_id=goal_id)

    record = result.single()
    if record:
        print(f"\n找到路径！长度: {record['path_length']}")
        print(f"节点序列: {record['node_ids']}")
    else:
        print(f"\n在Neo4j中也找不到从 {start_id} 到 {goal_id} 的路径")

    # 选择一个有双向连接的示例
    print("\n" + "=" * 60)
    print("查找StandPoint和RunwayPoint之间的连接:")
    result = session.run("""
        MATCH (a:StandPoint)-[r]->(b:RunwayPoint)
        RETURN id(a) AS stand_id, id(b) AS runway_id, type(r) AS rel_type
        LIMIT 5
    """)

    for record in result:
        print(f"  StandPoint[{record['stand_id']}] --[{record['rel_type']}]--> RunwayPoint[{record['runway_id']}]")

driver.close()
