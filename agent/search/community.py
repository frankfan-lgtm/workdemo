"""
社区灵感搜索
搜索其他用户在即梦社区发布的优质创作
"""

from dataclasses import dataclass


@dataclass
class CommunityResult:
    title: str
    author: str
    prompt: str
    image_url: str
    likes: int
    tags: list[str]
    source: str = "community"


# 模拟社区数据
MOCK_COMMUNITY_DATA = [
    CommunityResult(
        title="梦幻水下世界",
        author="创意小达人",
        prompt="水下珊瑚礁，五彩斑斓的热带鱼群，阳光透过海面折射，梦幻般的蓝色调",
        image_url="https://picsum.photos/seed/comm1/400/400",
        likes=2345,
        tags=["水下", "梦幻", "自然", "治愈"],
    ),
    CommunityResult(
        title="机械朋克少女",
        author="ACG_Master",
        prompt="赛博朋克风格机械少女，精密的金属零件与人体融合，发光的蓝色瞳孔",
        image_url="https://picsum.photos/seed/comm2/400/400",
        likes=5678,
        tags=["赛博朋克", "二次元", "科幻", "人物"],
    ),
    CommunityResult(
        title="新中式庭院",
        author="设计师阿花",
        prompt="新中式风格庭院设计，竹林、假山、水景，现代建筑与传统元素融合",
        image_url="https://picsum.photos/seed/comm3/400/400",
        likes=3210,
        tags=["新中式", "建筑", "设计", "庭院"],
    ),
    CommunityResult(
        title="复古胶片写真",
        author="摄影爱好者",
        prompt="90年代复古胶片风格写真，温暖的色调，颗粒感，街头随拍",
        image_url="https://picsum.photos/seed/comm4/400/400",
        likes=4567,
        tags=["复古", "胶片", "写真", "街拍"],
    ),
    CommunityResult(
        title="电商3C产品图",
        author="电商设计Pro",
        prompt="高端耳机产品图，深色背景，rim light勾勒轮廓，悬浮效果",
        image_url="https://picsum.photos/seed/comm5/400/400",
        likes=1890,
        tags=["电商", "3C", "产品", "商业"],
    ),
    CommunityResult(
        title="日式动漫场景",
        author="动漫爱好者",
        prompt="宫崎骏风格的乡村夏日场景，蓝天白云、向日葵田、古朴的日式小屋",
        image_url="https://picsum.photos/seed/comm6/400/400",
        likes=6789,
        tags=["动漫", "日系", "场景", "治愈"],
    ),
    CommunityResult(
        title="时尚大片",
        author="Fashion_AI",
        prompt="高级时装杂志风格，模特穿着avant-garde设计，戏剧性打光",
        image_url="https://picsum.photos/seed/comm7/400/400",
        likes=3456,
        tags=["时尚", "大片", "模特", "高级"],
    ),
    CommunityResult(
        title="电影海报概念图",
        author="影视概念师",
        prompt="科幻电影海报概念图，太空站背景，宇航员剪影，壮丽星空",
        image_url="https://picsum.photos/seed/comm8/400/400",
        likes=4321,
        tags=["电影", "海报", "科幻", "概念"],
    ),
]


async def search_community(query: str, intent: str = "通用", top_k: int = 5) -> list[CommunityResult]:
    """
    搜索社区发布的灵感作品
    Demo: 关键词 + 标签匹配
    生产环境: 多模态embedding语义检索
    """
    query_lower = query.lower()
    scored = []

    for item in MOCK_COMMUNITY_DATA:
        score = 0.0
        query_words = query_lower.replace("，", " ").replace(",", " ").split()
        for word in query_words:
            if len(word) >= 2:
                if word in item.title:
                    score += 0.3
                if word in item.prompt:
                    score += 0.2
                if word in item.tags:
                    score += 0.35
        # 热度加分
        score += min(item.likes / 10000, 0.1)
        scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
