"""
机场场面滑行轨迹优化 - 天气服务模块
=====================================

功能：
1. 接入高德天气API，获取实时天气数据
2. 将天气现象映射为滑行速度折扣系数
3. 提供天气缓存机制，避免频繁调用API
4. 支持天气对A*算法路径规划的影响量化

参考文献：
1. 寇伟彬等(2024) - 韧性导向的机场航空器滑行路径及停机位分配联合优化
2. Park & Kim - 机场天气对滑行时间影响的排队模型分析
3. 香港机场(2020) - 深度学习滑行时间预测中的天气因素分析

天气影响量化方法（速度折扣系数）：
- 晴/多云/阴：1.00（正常滑行速度）
- 阵雨/小雨：0.85（减速15%，路面轻微湿滑）
- 雷阵雨/中雨：0.70（减速30%，能见度降低）
- 大雨：0.55（减速45%，严重湿滑）
- 暴雨/雪/雾/霾：0.40（减速60%，极低能见度）

作者：毕业设计项目
日期：2026
"""

import requests
import time
import os
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class WeatherInfo:
    """天气信息数据类"""
    city: str = "西安市"
    adcode: str = "610100"
    weather: str = "晴"
    temperature: str = "25"
    winddirection: str = "无"
    windpower: str = "≤3"
    humidity: str = "50"
    reporttime: str = ""
    
    # 衍生字段
    weather_factor: float = 1.0  # 速度折扣系数
    weather_level: str = "normal"  # 天气等级：normal/moderate/severe/extreme
    visibility_impact: str = "none"  # 能见度影响：none/moderate/severe
    
    def to_dict(self) -> Dict:
        """转换为字典，用于JSON序列化"""
        return {
            'city': self.city,
            'adcode': self.adcode,
            'weather': self.weather,
            'temperature': self.temperature,
            'winddirection': self.winddirection,
            'windpower': self.windpower,
            'humidity': self.humidity,
            'reporttime': self.reporttime,
            'weather_factor': self.weather_factor,
            'weather_level': self.weather_level,
            'visibility_impact': self.visibility_impact
        }


class WeatherService:
    """
    天气服务类
    
    负责：
    - 调用高德天气API获取实时天气
    - 将天气现象转换为滑行速度折扣系数
    - 缓存天气数据，控制API调用频率
    """
    
    # 高德天气API接口地址
    WEATHER_API_URL = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    # 天气现象 -> 速度折扣系数映射表
    # 基于文献调研结果（寇伟彬2024、Park&Kim、香港机场2020）
    WEATHER_FACTOR_MAP = {
        # 良好天气
        '晴': 1.00,
        '多云': 1.00,
        '阴': 0.95,
        '少云': 0.95,
        
        # 轻度影响
        '雨': 0.80,
        '阵雨': 0.85,
        '小雨': 0.85,
        '雨夹雪': 0.80,
        
        # 中度影响
        '雷阵雨': 0.70,
        '中雨': 0.70,
        '小雪': 0.75,
        
        # 严重影响
        '大雨': 0.55,
        '暴雨': 0.40,
        '大暴雨': 0.35,
        '特大暴雨': 0.30,
        '中雪': 0.50,
        '雪': 0.50,
        '大雪': 0.40,
        '暴雪': 0.30,
        
        # 能见度极低
        '雾': 0.40,
        '霾': 0.45,
        '浮尘': 0.50,
        '扬沙': 0.50,
        '沙尘暴': 0.35,
        
        # 强对流
        '冰雹': 0.35,
        '龙卷风': 0.20,
        '台风': 0.25,
    }
    
    # 天气等级划分
    WEATHER_LEVEL_MAP = {
        '晴': 'normal',
        '多云': 'normal',
        '阴': 'normal',
        '少云': 'normal',
        '雨': 'moderate',
        '阵雨': 'moderate',
        '小雨': 'moderate',
        '雨夹雪': 'moderate',
        '雷阵雨': 'severe',
        '中雨': 'severe',
        '小雪': 'moderate',
        '大雨': 'severe',
        '暴雨': 'extreme',
        '大暴雨': 'extreme',
        '特大暴雨': 'extreme',
        '中雪': 'severe',
        '大雪': 'extreme',
        '暴雪': 'extreme',
        '雾': 'extreme',
        '霾': 'severe',
        '浮尘': 'severe',
        '扬沙': 'severe',
        '沙尘暴': 'extreme',
        '冰雹': 'extreme',
        '龙卷风': 'extreme',
        '台风': 'extreme',
    }
    
    def __init__(self, api_key: Optional[str] = None, 
                 city_adcode: str = "610100",
                 cache_seconds: int = 600):
        """
        初始化天气服务
        
        参数:
            api_key: 高德API Key，如果为None则从环境变量读取
            city_adcode: 城市编码（西安=610100）
            cache_seconds: 缓存时间（秒），默认10分钟
        """
        self.api_key = api_key or os.getenv('AMAP_API_KEY', 'YOUR_AMAP_KEY_HERE')
        self.city_adcode = city_adcode
        self.cache_seconds = cache_seconds
        
        # 缓存
        self._cached_weather: Optional[WeatherInfo] = None
        self._cache_timestamp: float = 0
        
        # 默认天气（API不可用时的回退）
        self._default_weather = WeatherInfo()
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._cached_weather is None:
            return False
        elapsed = time.time() - self._cache_timestamp
        return elapsed < self.cache_seconds
    
    def _parse_weather_response(self, data: Dict) -> WeatherInfo:
        """
        解析高德天气API响应
        
        参数:
            data: API返回的JSON数据
            
        返回:
            WeatherInfo对象
        """
        lives = data.get('lives', [])
        if not lives:
            return self._default_weather
        
        live = lives[0]
        weather_str = live.get('weather', '晴')
        
        # 获取速度折扣系数
        weather_factor = self.WEATHER_FACTOR_MAP.get(weather_str, 1.0)
        weather_level = self.WEATHER_LEVEL_MAP.get(weather_str, 'normal')
        
        # 能见度影响判断
        if weather_factor >= 0.85:
            visibility_impact = 'none'
        elif weather_factor >= 0.60:
            visibility_impact = 'moderate'
        else:
            visibility_impact = 'severe'
        
        return WeatherInfo(
            city=live.get('city', '西安市'),
            adcode=live.get('adcode', '610100'),
            weather=weather_str,
            temperature=live.get('temperature', '25'),
            winddirection=live.get('winddirection', '无'),
            windpower=live.get('windpower', '≤3'),
            humidity=live.get('humidity', '50'),
            reporttime=live.get('reporttime', ''),
            weather_factor=weather_factor,
            weather_level=weather_level,
            visibility_impact=visibility_impact
        )
    
    def get_current_weather(self, force_refresh: bool = False) -> WeatherInfo:
        """
        获取当前天气
        
        参数:
            force_refresh: 是否强制刷新缓存
            
        返回:
            WeatherInfo对象
        """
        # 检查缓存
        if not force_refresh and self._is_cache_valid():
            return self._cached_weather
        
        # API Key未设置，返回默认天气
        if not self.api_key or self.api_key == 'YOUR_AMAP_KEY_HERE':
            print("[WeatherService] 警告: 高德API Key未设置，使用默认天气数据")
            return self._default_weather
        
        try:
            # 调用高德天气API
            params = {
                'key': self.api_key,
                'city': self.city_adcode,
                'extensions': 'base'  # 获取实时天气
            }
            
            response = requests.get(self.WEATHER_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查API返回状态
            if data.get('status') != '1':
                error_info = data.get('info', '未知错误')
                print(f"[WeatherService] 天气API错误: {error_info}")
                return self._cached_weather or self._default_weather
            
            # 解析天气数据
            weather = self._parse_weather_response(data)
            
            # 更新缓存
            self._cached_weather = weather
            self._cache_timestamp = time.time()
            
            print(f"[WeatherService] 天气更新: {weather.city} {weather.weather} "
                  f"{weather.temperature}°C 风速{weather.windpower}级 "
                  f"折扣系数:{weather.weather_factor}")
            
            return weather
            
        except requests.exceptions.RequestException as e:
            print(f"[WeatherService] 网络请求失败: {e}")
            # 网络错误时返回缓存或默认数据
            return self._cached_weather or self._default_weather
        except Exception as e:
            print(f"[WeatherService] 获取天气异常: {e}")
            return self._cached_weather or self._default_weather
    
    def get_weather_factor(self, weather_type: Optional[str] = None) -> float:
        """
        获取指定天气类型的速度折扣系数
        
        参数:
            weather_type: 天气类型，如果为None则获取当前实时天气的系数
            
        返回:
            速度折扣系数 (0.0 ~ 1.0)
        """
        if weather_type is None:
            weather = self.get_current_weather()
            return weather.weather_factor
        return self.WEATHER_FACTOR_MAP.get(weather_type, 1.0)
    
    def get_weather_for_path_planning(self) -> Dict:
        """
        获取用于路径规划的天气信息
        
        返回:
            包含weather_factor、weather_level等关键字段的字典
        """
        weather = self.get_current_weather()
        return {
            'weather_factor': weather.weather_factor,
            'weather_level': weather.weather_level,
            'visibility_impact': weather.visibility_impact,
            'weather_description': weather.weather,
            'temperature': weather.temperature,
            'wind_power': weather.windpower,
            'raw': weather.to_dict()
        }


# 全局天气服务实例（单例模式）
_weather_service_instance: Optional[WeatherService] = None


def get_weather_service(api_key: Optional[str] = None,
                        city_adcode: str = "610100") -> WeatherService:
    """
    获取全局天气服务实例（单例）
    
    参数:
        api_key: 高德API Key
        city_adcode: 城市编码
        
    返回:
        WeatherService实例
    """
    global _weather_service_instance
    if _weather_service_instance is None:
        _weather_service_instance = WeatherService(
            api_key=api_key,
            city_adcode=city_adcode
        )
    return _weather_service_instance


def reset_weather_service():
    """重置天气服务实例（用于测试）"""
    global _weather_service_instance
    _weather_service_instance = None


# 演示
def demo_weather_service():
    """演示天气服务功能"""
    print("=" * 70)
    print("天气服务模块演示")
    print("=" * 70)
    
    # 创建天气服务实例（使用默认配置）
    service = WeatherService()
    
    print("\n1. 获取当前天气（API Key未设置时将返回默认数据）:")
    weather = service.get_current_weather()
    print(f"   城市: {weather.city}")
    print(f"   天气: {weather.weather}")
    print(f"   温度: {weather.temperature}°C")
    print(f"   风向: {weather.winddirection}")
    print(f"   风力: {weather.windpower}")
    print(f"   湿度: {weather.humidity}%")
    
    print("\n2. 天气影响因子:")
    print(f"   速度折扣系数: {weather.weather_factor}")
    print(f"   天气等级: {weather.weather_level}")
    print(f"   能见度影响: {weather.visibility_impact}")
    
    print("\n3. 各天气类型折扣系数表:")
    test_weathers = ['晴', '多云', '小雨', '中雨', '大雨', '暴雨', '雾', '雪']
    for w in test_weathers:
        factor = service.get_weather_factor(w)
        print(f"   {w}: {factor}")
    
    print("\n4. 路径规划用天气信息:")
    planning_info = service.get_weather_for_path_planning()
    for key, value in planning_info.items():
        if key != 'raw':
            print(f"   {key}: {value}")


if __name__ == "__main__":
    demo_weather_service()
