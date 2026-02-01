"""
测试API服务是否正常运行
"""

import requests
import time

def test_api():
    base_url = "http://localhost:5001"

    print("=" * 60)
    print("测试A*算法API服务")
    print("=" * 60)

    try:
        # 测试首页
        print("\n1. 测试首页...")
        response = requests.get(f"{base_url}/")
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")

        # 测试健康检查
        print("\n2. 测试健康检查...")
        response = requests.get(f"{base_url}/api/health")
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   状态: {data['status']}")
        print(f"   节点数: {data['node_count']}")
        print(f"   边数: {data['edge_count']}")

        # 测试获取节点
        print("\n3. 测试获取所有节点...")
        response = requests.get(f"{base_url}/api/nodes")
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   成功: {data['success']}")
        print(f"   节点数: {data['count']}")

        # 测试获取最远机位
        print("\n4. 测试获取最远机位对...")
        response = requests.get(f"{base_url}/api/demo/farthest-stand")
        print(f"   状态码: {response.status_code}")
        data = response.json()
        if data['success']:
            print(f"   起点: {data['start_node']['id']}")
            print(f"   终点: {data['goal_node']['id']}")
            print(f"   距离: {data['distance']:.2f} 米")

            # 测试路径计算
            print("\n5. 测试路径计算...")
            path_response = requests.post(
                f"{base_url}/api/path",
                json={
                    "start_node_id": data['start_node']['id'],
                    "goal_node_id": data['goal_node']['id']
                }
            )
            print(f"   状态码: {path_response.status_code}")
            path_data = path_response.json()
            if path_data['success']:
                stats = path_data['stats']
                print(f"   找到路径！")
                print(f"   路径长度: {stats['total_distance']:.2f} 米")
                print(f"   预计时间: {stats['total_time']:.2f} 秒")
                print(f"   路径节点数: {stats['num_nodes']}")
            else:
                print(f"   错误: {path_data.get('error')}")
        else:
            print(f"   错误: {data.get('error')}")

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到API服务")
        print("请确保Flask服务已启动: python api.py")
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")

if __name__ == "__main__":
    test_api()
