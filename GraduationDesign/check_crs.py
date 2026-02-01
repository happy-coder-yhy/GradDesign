"""检查SHP文件的坐标系统"""
import geopandas as gpd
from pathlib import Path

base_path = Path("/Users/xupeihong/Desktop/毕业设计/demo/GraduationDesign/西安机场")

# 检查几个SHP文件的坐标系统
shp_files = [
    "西安机场机位和道路SHP/机位点.shp",
    "西安机场路网数据/network/network.shp",
    "西安机场机位和道路SHP/线路_航空器.shp"
]

for shp_file in shp_files:
    full_path = base_path / shp_file
    if full_path.exists():
        gdf = gpd.read_file(full_path)
        print(f"\n{shp_file}:")
        print(f"  CRS: {gdf.crs}")
        print(f"  示例坐标: {gdf.iloc[0].geometry if len(gdf) > 0 else 'N/A'}")
        print(f"  边界范围: {gdf.total_bounds}")
