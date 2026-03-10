"""
RAG 优质数据库搜索
模拟从已建立的优质训练数据 RAG 库中搜索相关素材
包含高质量图片+caption，用于启发创作灵感
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RAGResult:
    title: str
    caption: str
    image_url: str
    tags: list[str]
    quality_score: float  # 0-1
    source: str = "rag"


# 模拟的RAG库数据
MOCK_RAG_DATA = [
    RAGResult(
        title="梦幻森林晨光",
        caption="清晨阳光穿过薄雾笼罩的森林，金色光束在树叶间散射，地面覆盖着青苔和野花，整体氛围宁静而神秘",
        image_url="https://picsum.photos/seed/rag1/400/400",
        tags=["森林", "晨光", "自然", "氛围感", "治愈"],
        quality_score=0.95,
    ),
    RAGResult(
        title="赛博朋克城市夜景",
        caption="未来感十足的城市夜景，霓虹灯映照在雨水浸湿的街道上，高楼大厦间穿梭的飞行器，蓝紫色调为主",
        image_url="https://picsum.photos/seed/rag2/400/400",
        tags=["赛博朋克", "科幻", "城市", "夜景", "未来"],
        quality_score=0.92,
    ),
    RAGResult(
        title="极简产品展示",
        caption="白色大理石台面上摆放的护肤品，柔和的侧光照明，浅色调背景，极简主义构图，突出产品质感",
        image_url="https://picsum.photos/seed/rag3/400/400",
        tags=["产品", "极简", "电商", "护肤品", "白底"],
        quality_score=0.90,
    ),
    RAGResult(
        title="国风水墨山水",
        caption="传统中国水墨画风格的山水画面，远山如黛、近水含烟，留白大方，意境深远",
        image_url="https://picsum.photos/seed/rag4/400/400",
        tags=["国风", "水墨", "山水", "传统", "艺术"],
        quality_score=0.94,
    ),
    RAGResult(
        title="时尚街拍",
        caption="模特身穿oversized西装走在东京街头，樱花飘落，电影感色调，低饱和度高质感",
        image_url="https://picsum.photos/seed/rag5/400/400",
        tags=["街拍", "时尚", "穿搭", "日系", "电影感"],
        quality_score=0.88,
    ),
    RAGResult(
        title="美食特写摄影",
        caption="精致的法式甜点特写，覆盆子挞配金箔装饰，浅景深微距拍摄，暖色调灯光",
        image_url="https://picsum.photos/seed/rag6/400/400",
        tags=["美食", "甜点", "摄影", "特写", "精致"],
        quality_score=0.91,
    ),
    RAGResult(
        title="电影级人像",
        caption="暗调电影风格人像，窗户透入的丁达尔光效，人物面部半明半暗，情绪感强烈",
        image_url="https://picsum.photos/seed/rag7/400/400",
        tags=["人像", "电影", "影视", "光影", "情绪"],
        quality_score=0.93,
    ),
    RAGResult(
        title="3D产品渲染",
        caption="C4D风格的3D产品渲染，彩色玻璃材质球体，柔和渐变背景，品牌感十足",
        image_url="https://picsum.photos/seed/rag8/400/400",
        tags=["3D", "渲染", "品牌", "设计", "C4D"],
        quality_score=0.89,
    ),
    RAGResult(
        title="航拍自然地貌",
        caption="冰岛黑沙滩航拍，蜿蜒的河流在火山灰地面上形成抽象图案，自然的几何美学",
        image_url="https://picsum.photos/seed/rag9/400/400",
        tags=["航拍", "自然", "冰岛", "抽象", "地貌"],
        quality_score=0.96,
    ),
    RAGResult(
        title="复古胶片风格",
        caption="充满颗粒感的胶片风格照片，咖啡馆午后阳光，带有轻微漏光效果，怀旧温馨",
        image_url="https://picsum.photos/seed/rag10/400/400",
        tags=["复古", "胶片", "怀旧", "咖啡", "氛围"],
        quality_score=0.87,
    ),
]


async def search_rag(query: str, intent: str = "通用", top_k: int = 5) -> list[RAGResult]:
    """
    从RAG库搜索优质参考素材
    Demo: 基于关键词匹配模拟语义搜索
    生产环境: 使用多模态embedding进行向量检索
    """
    query_lower = query.lower()
    scored_results = []

    for item in MOCK_RAG_DATA:
        score = 0.0
        # 标签匹配
        for tag in item.tags:
            if tag in query_lower:
                score += 0.3
        # caption 关键词匹配
        query_words = query_lower.replace("，", " ").replace(",", " ").split()
        for word in query_words:
            if len(word) >= 2 and word in item.caption:
                score += 0.2
        # 意图匹配
        intent_tag_map = {
            "电商": ["产品", "电商", "白底", "极简"],
            "流量照片": ["街拍", "时尚", "穿搭", "氛围", "日系"],
            "艺术创作": ["艺术", "水墨", "国风", "赛博朋克", "科幻"],
            "品牌设计": ["品牌", "设计", "3D", "渲染", "C4D"],
            "影视": ["电影", "影视", "光影", "情绪"],
        }
        for tag in item.tags:
            if tag in intent_tag_map.get(intent, []):
                score += 0.25

        # 加上基础质量分
        score += item.quality_score * 0.1
        scored_results.append((score, item))

    scored_results.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored_results[:top_k]]
