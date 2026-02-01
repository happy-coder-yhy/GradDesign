from neo4j import GraphDatabase
import os
from dotenv import load_dotenv
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString
import json

# 加载环境变量
load_dotenv()


class Neo4jConnection:
    def __init__(self, uri, user, password):
        self.driver = None
        self.uri = uri
        self.user = user
        self.password = password

    def connect(self):
        """建立与Neo4j数据库的连接"""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print("成功连接到Neo4j数据库")
            return True
        except Exception as e:
            print(f"连接Neo4j数据库失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            print("已关闭Neo4j数据库连接")

    def test_connection(self):
        """测试连接并查询数据库信息"""
        if not self.driver:
            print("数据库未连接")
            return False

        try:
            with self.driver.session() as session:
                result = session.run("RETURN 'Hello, Neo4j!' AS greeting")
                record = result.single()
                print(f"数据库响应: {record['greeting']}")
                
                # 查询节点数量
                node_count = session.run("MATCH (n) RETURN count(n) AS count").single()['count']
                print(f"数据库中的节点总数: {node_count}")
                
                # 查询关系数量
                rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()['count']
                print(f"数据库中的关系总数: {rel_count}")
                
                # 查询各类型节点数量
                node_types = session.run("""
                    MATCH (n)
                    RETURN labels(n)[0] AS label, count(n) AS count
                    ORDER BY count DESC
                """)
                print("\n节点类型统计:")
                for record in node_types:
                    print(f"  {record['label']}: {record['count']} 个")
                
                return True
        except Exception as e:
            print(f"查询执行失败: {e}")
            return False

    def execute_query(self, query, parameters=None):
        """执行Cypher查询"""
        if not self.driver:
            print("数据库未连接")
            return None
            
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                return [dict(record) for record in result]
        except Exception as e:
            print(f"查询执行失败: {e}")
            return None

    def create_node(self, label, properties):
        """创建新节点"""
        query = f"CREATE (n:{label} $properties) RETURN n"
        try:
            with self.driver.session() as session:
                result = session.run(query, properties=properties)
                record = result.single()
                print(f"成功创建节点: {record['n']._properties}")
                return record['n']
        except Exception as e:
            print(f"创建节点失败: {e}")
            return None

    def find_nodes(self, label, properties=None):
        """查找指定标签和属性的节点"""
        if properties:
            conditions = " AND ".join([f"n.{key} = ${key}" for key in properties.keys()])
            query = f"MATCH (n:{label}) WHERE {conditions} RETURN n"
        else:
            query = f"MATCH (n:{label}) RETURN n"
            
        try:
            with self.driver.session() as session:
                result = session.run(query, **properties or {})
                nodes = [record['n'] for record in result]
                print(f"找到 {len(nodes)} 个节点")
                return nodes
        except Exception as e:
            print(f"查询节点失败: {e}")
            return []

    def clear_database(self):
        """清空数据库中的所有节点和关系"""
        if not self.driver:
            print("数据库未连接")
            return False
        
        try:
            with self.driver.session() as session:
                # 删除所有关系和节点
                session.run("MATCH (n) DETACH DELETE n")
                print("已清空数据库中的所有节点和关系")
                return True
        except Exception as e:
            print(f"清空数据库失败: {e}")
            return False

    def create_node_with_geometry(self, label, properties, geometry=None):
        """创建带几何信息的节点"""
        props = properties.copy()
        if geometry:
            # 将几何对象转换为WKT格式
            props['geometry'] = geometry.wkt
            if isinstance(geometry, Point):
                props['x'] = geometry.x
                props['y'] = geometry.y
        return self.create_node(label, props)

    def create_relationship(self, from_label, from_props, to_label, to_props, rel_type, rel_props=None):
        """创建两个节点之间的关系"""
        if not self.driver:
            print("数据库未连接")
            return False
        
        # 构建匹配条件
        from_conditions = " AND ".join([f"a.{key} = ${key}" for key in from_props.keys()])
        to_conditions = " AND ".join([f"b.{key} = ${key}" for key in to_props.keys()])
        
        # 构建关系属性
        rel_props_str = ""
        if rel_props:
            rel_props_str = " " + json.dumps(rel_props).replace('"', '').replace('{', '{').replace('}', '}')
        
        query = f"""
        MATCH (a:{from_label} WHERE {from_conditions})
        MATCH (b:{to_label} WHERE {to_conditions})
        MERGE (a)-[r:{rel_type} {rel_props_str}]->(b)
        RETURN r
        """
        
        try:
            with self.driver.session() as session:
                params = {**from_props, **to_props}
                result = session.run(query, params)
                return result.single() is not None
        except Exception as e:
            # 如果上面的查询失败，使用更简单的方式
            try:
                query = f"""
                MATCH (a:{from_label})
                MATCH (b:{to_label})
                WHERE {from_conditions.replace('a.', 'a.')} AND {to_conditions.replace('b.', 'b.')}
                MERGE (a)-[r:{rel_type}]->(b)
                RETURN r
                """
                with self.driver.session() as session:
                    params = {**from_props, **to_props}
                    result = session.run(query, params)
                    return result.single() is not None
            except Exception as e2:
                print(f"创建关系失败: {e2}")
                return False

    def import_shp_data(self, shp_path, node_label, geometry_type='auto'):
        """导入shp文件数据到Neo4j"""
        if not self.driver:
            print("数据库未连接")
            return False
        
        try:
            print(f"正在读取shp文件: {shp_path}")
            gdf = gpd.read_file(shp_path)
            print(f"成功读取 {len(gdf)} 条记录")
            
            # 确定几何类型
            if geometry_type == 'auto':
                if all(isinstance(geom, Point) for geom in gdf.geometry if geom is not None):
                    geometry_type = 'Point'
                elif all(isinstance(geom, LineString) for geom in gdf.geometry if geom is not None):
                    geometry_type = 'LineString'
                else:
                    geometry_type = 'Mixed'
            
            print(f"几何类型: {geometry_type}")
            
            # 批量创建节点
            batch_size = 1000
            total_created = 0
            
            with self.driver.session() as session:
                for idx in range(0, len(gdf), batch_size):
                    batch = gdf.iloc[idx:idx+batch_size]
                    nodes_data = []
                    
                    for _, row in batch.iterrows():
                        # 准备节点属性
                        props = {}
                        for col in gdf.columns:
                            if col != 'geometry':
                                val = row[col]
                                # 处理NaN值
                                if pd.isna(val):
                                    continue
                                # 转换数据类型
                                if isinstance(val, (int, float, str, bool)):
                                    props[col] = val
                        
                        # 添加几何信息
                        if row.geometry is not None:
                            props['geometry'] = row.geometry.wkt
                            if isinstance(row.geometry, Point):
                                props['x'] = row.geometry.x
                                props['y'] = row.geometry.y
                            elif isinstance(row.geometry, LineString):
                                # 对于线，存储起点和终点
                                coords = list(row.geometry.coords)
                                if len(coords) > 0:
                                    props['start_x'] = coords[0][0]
                                    props['start_y'] = coords[0][1]
                                if len(coords) > 1:
                                    props['end_x'] = coords[-1][0]
                                    props['end_y'] = coords[-1][1]
                        
                        nodes_data.append(props)
                    
                    # 批量创建节点
                    query = f"""
                    UNWIND $nodes AS node
                    CREATE (n:{node_label})
                    SET n = node
                    RETURN count(n) AS count
                    """
                    
                    result = session.run(query, nodes=nodes_data)
                    count = result.single()['count']
                    total_created += count
                    print(f"已创建 {total_created}/{len(gdf)} 个节点")
            
            print(f"成功导入 {total_created} 个 {node_label} 节点")
            return True
            
        except Exception as e:
            print(f"导入shp文件失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def build_network_graph(self, base_path):
        """构建路网图模型"""
        if not self.driver:
            print("数据库未连接")
            return False
        
        print("开始构建路网图模型...")
        
        # 定义shp文件路径和对应的节点标签
        shp_files = [
            # 路网数据
            (f"{base_path}/西安机场路网数据/network/network.shp", "Network"),
            (f"{base_path}/西安机场路网数据/runwaypoints/runwaypoints.shp", "RunwayPoint"),
            (f"{base_path}/西安机场路网数据/standpoints/standpoints.shp", "StandPoint"),
            # 机位和道路数据
            (f"{base_path}/西安机场机位和道路SHP/机位点.shp", "StandPoint"),
            (f"{base_path}/西安机场机位和道路SHP/线路_保障车辆.shp", "ServiceVehicleRoad"),
            (f"{base_path}/西安机场机位和道路SHP/线路_围场路.shp", "PerimeterRoad"),
            (f"{base_path}/西安机场机位和道路SHP/线路_场外.shp", "ExternalRoad"),
            (f"{base_path}/西安机场机位和道路SHP/线路_航空器.shp", "AircraftRoad"),
        ]
        
        # 导入所有shp文件
        for shp_path, label in shp_files:
            if os.path.exists(shp_path):
                self.import_shp_data(shp_path, label)
            else:
                print(f"警告: 文件不存在 {shp_path}")
        
        # 建立连接关系（基于几何位置）
        print("正在建立节点之间的连接关系...")
        self._build_spatial_relationships()
        
        print("路网图模型构建完成！")
        return True

    def _build_spatial_relationships(self, road_to_point_threshold=50, road_to_road_threshold=20, point_to_point_threshold=5):
        """基于空间位置建立节点之间的关系
        
        参数:
            road_to_point_threshold: 线路到点的距离阈值（默认50）
            road_to_road_threshold: 线路之间的距离阈值（默认20，更严格）
            point_to_point_threshold: 点之间的距离阈值（默认5，非常严格）
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                # 定义所有线路类型和点类型
                road_types = ['Network', 'ServiceVehicleRoad', 'AircraftRoad', 'PerimeterRoad', 'ExternalRoad']
                point_types = ['StandPoint', 'RunwayPoint']
                
                total_relationships = 0
                
                # 1. 连接线路的起点到最近的节点（只连接最近的1个）
                print("正在连接线路起点到最近的节点...")
                for road_type in road_types:
                    # 合并所有点类型，找到最近的节点
                    query = f"""
                    MATCH (road:{road_type})
                    WHERE road.start_x IS NOT NULL AND road.start_y IS NOT NULL
                    WITH road
                    MATCH (point)
                    WHERE (point:StandPoint OR point:RunwayPoint)
                      AND point.x IS NOT NULL AND point.y IS NOT NULL
                    WITH road, point,
                         sqrt((road.start_x - point.x)^2 + (road.start_y - point.y)^2) AS dist
                    WHERE dist < {road_to_point_threshold}
                    WITH road, point, dist
                    ORDER BY road, dist
                    WITH road, collect({{point: point, dist: dist}})[0] AS nearest
                    WHERE nearest IS NOT NULL
                    MERGE (road)-[r:STARTS_AT {{distance: nearest.dist}}]->(nearest.point)
                    ON CREATE SET r.created = true
                    RETURN count(*) AS count
                    """
                    try:
                        result = session.run(query)
                        count = result.single()['count']
                        if count > 0:
                            print(f"  建立了 {count} 个 {road_type} 起点到节点的关系")
                            total_relationships += count
                    except Exception as e:
                        print(f"  建立 {road_type} 起点关系时出错: {e}")
                
                # 2. 连接线路的终点到最近的节点（只连接最近的1个）
                print("正在连接线路终点到最近的节点...")
                for road_type in road_types:
                    query = f"""
                    MATCH (road:{road_type})
                    WHERE road.end_x IS NOT NULL AND road.end_y IS NOT NULL
                    WITH road
                    MATCH (point)
                    WHERE (point:StandPoint OR point:RunwayPoint)
                      AND point.x IS NOT NULL AND point.y IS NOT NULL
                    WITH road, point,
                         sqrt((road.end_x - point.x)^2 + (road.end_y - point.y)^2) AS dist
                    WHERE dist < {road_to_point_threshold}
                    WITH road, point, dist
                    ORDER BY road, dist
                    WITH road, collect({{point: point, dist: dist}})[0] AS nearest
                    WHERE nearest IS NOT NULL
                    MERGE (road)-[r:ENDS_AT {{distance: nearest.dist}}]->(nearest.point)
                    ON CREATE SET r.created = true
                    RETURN count(*) AS count
                    """
                    try:
                        result = session.run(query)
                        count = result.single()['count']
                        if count > 0:
                            print(f"  建立了 {count} 个 {road_type} 终点到节点的关系")
                            total_relationships += count
                    except Exception as e:
                        print(f"  建立 {road_type} 终点关系时出错: {e}")
                
                # 3. 连接线路之间（只连接真正相邻的线路，使用更小的阈值）
                print("正在连接相邻的线路...")
                # 只连接同类型或相关类型的线路，避免所有组合
                road_connections = [
                    ('Network', 'Network'),
                    ('ServiceVehicleRoad', 'ServiceVehicleRoad'),
                    ('AircraftRoad', 'AircraftRoad'),
                    ('PerimeterRoad', 'PerimeterRoad'),
                    ('ExternalRoad', 'ExternalRoad'),
                    ('Network', 'ServiceVehicleRoad'),  # 主要路网连接到服务车辆道路
                    ('Network', 'AircraftRoad'),  # 主要路网连接到航空器道路
                ]
                
                for road_type1, road_type2 in road_connections:
                    # 只连接：road1的终点接近road2的起点（单向，避免重复）
                    query = f"""
                    MATCH (road1:{road_type1}), (road2:{road_type2})
                    WHERE road1.end_x IS NOT NULL AND road1.end_y IS NOT NULL
                      AND road2.start_x IS NOT NULL AND road2.start_y IS NOT NULL
                      AND id(road1) <> id(road2)
                    WITH road1, road2,
                         sqrt((road1.end_x - road2.start_x)^2 + (road1.end_y - road2.start_y)^2) AS dist
                    WHERE dist < {road_to_road_threshold}
                    WITH road1, road2, dist
                    ORDER BY road1, dist
                    WITH road1, collect({{road: road2, dist: dist}})[0] AS nearest
                    WHERE nearest IS NOT NULL
                    MERGE (road1)-[r:CONNECTS_TO {{distance: nearest.dist}}]->(nearest.road)
                    ON CREATE SET r.created = true
                    RETURN count(*) AS count
                    """
                    try:
                        result = session.run(query)
                        count = result.single()['count']
                        if count > 0:
                            print(f"  建立了 {count} 个 {road_type1} 到 {road_type2} 的连接关系")
                            total_relationships += count
                    except Exception as e:
                        print(f"  建立 {road_type1} 到 {road_type2} 连接时出错: {e}")
                
                # 4. 可选：连接非常接近的点（阈值很小，只连接几乎重合的点）
                print("正在连接几乎重合的点（可选）...")
                # 只连接StandPoint和RunwayPoint之间非常接近的点
                query = f"""
                MATCH (p1:StandPoint), (p2:RunwayPoint)
                WHERE p1.x IS NOT NULL AND p1.y IS NOT NULL
                  AND p2.x IS NOT NULL AND p2.y IS NOT NULL
                  AND id(p1) <> id(p2)
                WITH p1, p2,
                     sqrt((p1.x - p2.x)^2 + (p1.y - p2.y)^2) AS dist
                WHERE dist < {point_to_point_threshold}
                MERGE (p1)-[r:NEAR {{distance: dist}}]->(p2)
                ON CREATE SET r.created = true
                RETURN count(*) AS count
                """
                try:
                    result = session.run(query)
                    count = result.single()['count']
                    if count > 0:
                        print(f"  建立了 {count} 个点之间的邻近关系")
                        total_relationships += count
                except Exception as e:
                    print(f"  建立点邻近关系时出错: {e}")
                
                print(f"\n总共建立了 {total_relationships} 个关系（边）")
                
                # 查询关系统计
                rel_query = """
                MATCH ()-[r]->()
                RETURN type(r) AS rel_type, count(r) AS count
                ORDER BY count DESC
                """
                result = session.run(rel_query)
                print("\n关系类型统计:")
                for record in result:
                    print(f"  {record['rel_type']}: {record['count']} 条")
        
        except Exception as e:
            print(f"建立空间关系失败: {e}")
            import traceback
            traceback.print_exc()


def main():
    # 从环境变量或默认值获取连接参数
    neo4j_uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    neo4j_user = os.getenv('NEO4J_USER', 'neo4j')
    neo4j_password = os.getenv('NEO4J_PASSWORD', 'yhy2004117')

    # 创建数据库连接实例
    conn = Neo4jConnection(neo4j_uri, neo4j_user, neo4j_password)
    
    # 连接数据库
    if conn.connect():
        # 测试连接
        conn.test_connection()
        
        # 清空数据库
        print("\n正在清空数据库...")
        conn.clear_database()
        
        # 构建路网图模型
        base_path = os.path.join(os.path.dirname(__file__), "西安机场")
        print(f"\n开始读取shp文件并构建图模型...")
        print(f"数据路径: {base_path}")
        conn.build_network_graph(base_path)
        
        # 查询统计信息
        print("\n图模型统计信息:")
        conn.test_connection()
        
        conn.close()


if __name__ == "__main__":
    main()
    