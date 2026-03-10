"""
搜索路由器
根据意图分析结果，并行调度多个搜索源，汇总并排序结果
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from agent.intent import IntentResult, SearchSource
from agent.search.doubao_web import WebSearchResult, search_web
from agent.search.rag import RAGResult, search_rag
from agent.search.user_assets import UserAssetResult, search_user_assets
from agent.search.community import CommunityResult, search_community


@dataclass
class SearchResultItem:
    """统一的搜索结果格式"""
    title: str
    description: str
    image_url: str
    source: str       # doubao_web / rag / user_assets / community
    source_label: str  # 用于UI展示的中文标签
    extra: dict = field(default_factory=dict)


SOURCE_LABELS = {
    "doubao_web": "联网搜索",
    "rag": "优质素材库",
    "user_assets": "我的资产",
    "community": "社区灵感",
}


def _normalize_web(results: list[WebSearchResult]) -> list[SearchResultItem]:
    return [
        SearchResultItem(
            title=r.title,
            description=r.snippet,
            image_url=r.image_url,
            source="doubao_web",
            source_label=SOURCE_LABELS["doubao_web"],
            extra={"url": r.url},
        )
        for r in results
    ]


def _normalize_rag(results: list[RAGResult]) -> list[SearchResultItem]:
    return [
        SearchResultItem(
            title=r.title,
            description=r.caption,
            image_url=r.image_url,
            source="rag",
            source_label=SOURCE_LABELS["rag"],
            extra={"tags": r.tags, "quality_score": r.quality_score},
        )
        for r in results
    ]


def _normalize_user_assets(results: list[UserAssetResult]) -> list[SearchResultItem]:
    type_map = {"generated": "AI生成", "downloaded": "已下载", "favorited": "已收藏"}
    return [
        SearchResultItem(
            title=r.title,
            description=r.prompt,
            image_url=r.image_url,
            source="user_assets",
            source_label=SOURCE_LABELS["user_assets"],
            extra={"asset_type": type_map.get(r.asset_type, r.asset_type), "created_at": r.created_at},
        )
        for r in results
    ]


def _normalize_community(results: list[CommunityResult]) -> list[SearchResultItem]:
    return [
        SearchResultItem(
            title=r.title,
            description=r.prompt,
            image_url=r.image_url,
            source="community",
            source_label=SOURCE_LABELS["community"],
            extra={"author": r.author, "likes": r.likes, "tags": r.tags},
        )
        for r in results
    ]


@dataclass
class AggregatedSearchResult:
    """聚合后的搜索结果"""
    intent: IntentResult
    results_by_source: dict[str, list[SearchResultItem]] = field(default_factory=dict)
    summary: str = ""


async def route_and_search(intent: IntentResult) -> AggregatedSearchResult:
    """
    根据意图结果并行调度多个搜索源
    """
    query = intent.search_query
    creative_intent = intent.creative_intent.value
    tasks = {}

    for source in intent.search_sources:
        if source == SearchSource.DOUBAO_WEB:
            tasks["doubao_web"] = search_web(query, creative_intent)
        elif source == SearchSource.RAG:
            tasks["rag"] = search_rag(query, creative_intent)
        elif source == SearchSource.USER_ASSETS:
            tasks["user_assets"] = search_user_assets(query)
        elif source == SearchSource.COMMUNITY:
            tasks["community"] = search_community(query, creative_intent)

    # 并行执行所有搜索
    keys = list(tasks.keys())
    raw_results = await asyncio.gather(*tasks.values())

    # 归一化结果
    normalizers = {
        "doubao_web": _normalize_web,
        "rag": _normalize_rag,
        "user_assets": _normalize_user_assets,
        "community": _normalize_community,
    }

    results_by_source = {}
    for key, raw in zip(keys, raw_results):
        normalized = normalizers[key](raw)
        if normalized:
            results_by_source[key] = normalized

    # 生成摘要
    total = sum(len(v) for v in results_by_source.values())
    source_info = "、".join(SOURCE_LABELS.get(k, k) for k in results_by_source)
    summary = (
        f"识别到 [{creative_intent}] 创作意图，"
        f"已从 {source_info} 共找到 {total} 个相关参考素材。"
    )

    return AggregatedSearchResult(
        intent=intent,
        results_by_source=results_by_source,
        summary=summary,
    )
