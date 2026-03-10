"""
用户资产搜索
搜索用户在即梦平台生成、下载、收藏的图片
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserAssetResult:
    title: str
    prompt: str
    image_url: str
    asset_type: str  # generated / downloaded / favorited
    created_at: str
    source: str = "user_assets"


# 模拟用户资产数据
MOCK_USER_ASSETS = [
    UserAssetResult(
        title="我的电商产品图-护肤品",
        prompt="一瓶精华液放在大理石台面上，柔和自然光，极简风格",
        image_url="https://picsum.photos/seed/user1/400/400",
        asset_type="generated",
        created_at="2026-03-08",
    ),
    UserAssetResult(
        title="国风插画-山水",
        prompt="中国传统山水画风格，云雾缭绕的山峰，水墨画",
        image_url="https://picsum.photos/seed/user2/400/400",
        asset_type="generated",
        created_at="2026-03-05",
    ),
    UserAssetResult(
        title="收藏-赛博朋克城市",
        prompt="赛博朋克风格城市夜景，霓虹灯，雨夜",
        image_url="https://picsum.photos/seed/user3/400/400",
        asset_type="favorited",
        created_at="2026-03-03",
    ),
    UserAssetResult(
        title="下载-人像写真",
        prompt="电影级人像写真，暖色调，自然光线",
        image_url="https://picsum.photos/seed/user4/400/400",
        asset_type="downloaded",
        created_at="2026-03-01",
    ),
    UserAssetResult(
        title="我的logo设计稿",
        prompt="极简logo设计，几何图形，黑白配色",
        image_url="https://picsum.photos/seed/user5/400/400",
        asset_type="generated",
        created_at="2026-02-28",
    ),
    UserAssetResult(
        title="收藏-美食摄影",
        prompt="精致日式料理摆盘，俯拍视角，自然光",
        image_url="https://picsum.photos/seed/user6/400/400",
        asset_type="favorited",
        created_at="2026-02-25",
    ),
]


async def search_user_assets(query: str, top_k: int = 5) -> list[UserAssetResult]:
    """
    搜索用户个人资产
    Demo: 基于关键词匹配
    生产环境: 多模态embedding向量检索，考虑vlm成本先支持文字搜索
    """
    query_lower = query.lower()
    scored = []
    for asset in MOCK_USER_ASSETS:
        score = 0.0
        query_words = query_lower.replace("，", " ").replace(",", " ").split()
        for word in query_words:
            if len(word) >= 2:
                if word in asset.title:
                    score += 0.4
                if word in asset.prompt:
                    score += 0.3
        scored.append((score, asset))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]
