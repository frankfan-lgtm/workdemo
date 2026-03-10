"""
意图识别模块
根据用户输入判断：1) 是否需要搜索 2) 应该搜索哪些源 3) 搜索意图分类
"""

import re
from dataclasses import dataclass, field
from enum import Enum


class SearchSource(str, Enum):
    DOUBAO_WEB = "doubao_web"        # 豆包联网搜索
    RAG = "rag"                       # 优质数据RAG库
    USER_ASSETS = "user_assets"       # 用户自己的资产（生成/下载/收藏）
    COMMUNITY = "community"           # 社区发布的灵感图片


class CreativeIntent(str, Enum):
    ECOMMERCE = "电商"           # 电商产品图
    TRENDING_PHOTO = "流量照片"   # 社交媒体流量照片
    ART_CREATION = "艺术创作"     # 艺术/插画创作
    BRAND_DESIGN = "品牌设计"     # 品牌/logo/VI设计
    FILM_VIDEO = "影视"          # 影视/短视频
    GENERAL = "通用"             # 通用创作


@dataclass
class IntentResult:
    need_search: bool = False
    creative_intent: CreativeIntent = CreativeIntent.GENERAL
    search_sources: list[SearchSource] = field(default_factory=list)
    search_query: str = ""
    reasoning: str = ""


# 意图关键词映射
INTENT_KEYWORDS = {
    CreativeIntent.ECOMMERCE: [
        "电商", "产品图", "商品", "淘宝", "京东", "详情页", "主图",
        "白底图", "场景图", "模特", "产品展示", "商拍", "带货"
    ],
    CreativeIntent.TRENDING_PHOTO: [
        "小红书", "ins", "网红", "打卡", "氛围感", "写真", "日系",
        "韩系", "街拍", "穿搭", "vlog", "朋友圈", "头像", "壁纸"
    ],
    CreativeIntent.ART_CREATION: [
        "插画", "油画", "水彩", "素描", "概念art", "CG", "二次元",
        "动漫", "漫画", "国风", "赛博朋克", "奇幻", "科幻", "超现实"
    ],
    CreativeIntent.BRAND_DESIGN: [
        "logo", "品牌", "VI", "海报", "banner", "名片", "包装",
        "字体", "排版", "宣传", "广告", "营销", "物料"
    ],
    CreativeIntent.FILM_VIDEO: [
        "电影", "影视", "分镜", "场景", "特效", "短片", "MV",
        "剧照", "概念图", "气氛图", "故事板", "影调"
    ],
}

# 搜索触发关键词 — 明确表示需要参考/搜索的词
SEARCH_TRIGGER_WORDS = [
    "参考", "搜索", "找", "类似", "风格", "灵感", "借鉴",
    "像", "看看", "有没有", "推荐", "想要", "帮我找",
    "trending", "最新", "流行", "热门", "同款", "模仿",
]

# 不需要搜索的情况 — 纯生成指令
NO_SEARCH_WORDS = [
    "生成一", "画一", "创建一", "做一个", "帮我画", "帮我生成",
]


def analyze_intent(user_input: str, context: str = "") -> IntentResult:
    """
    基于规则 + 关键词的意图分析（demo 版本）
    生产环境应替换为 LLM 调用
    """
    combined = f"{user_input} {context}".lower()
    result = IntentResult()
    result.search_query = user_input

    # 1. 判断是否需要搜索
    has_search_trigger = any(w in combined for w in SEARCH_TRIGGER_WORDS)
    has_no_search = any(w in combined for w in NO_SEARCH_WORDS)

    if has_no_search and not has_search_trigger:
        result.need_search = False
        result.reasoning = "用户意图为直接生成，无需搜索参考素材"
        return result

    # 默认大部分创作场景都需要搜索辅助
    result.need_search = True

    # 2. 识别创作意图
    intent_scores: dict[CreativeIntent, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            intent_scores[intent] = score

    if intent_scores:
        result.creative_intent = max(intent_scores, key=intent_scores.get)
    else:
        result.creative_intent = CreativeIntent.GENERAL

    # 3. 根据意图决定搜索源
    sources = []

    # 如果提到"我的"、"之前"、"上次" → 用户资产
    if any(w in combined for w in ["我的", "之前", "上次", "我生成", "我收藏", "我下载"]):
        sources.append(SearchSource.USER_ASSETS)

    # 如果提到"社区"、"别人"、"热门"、"灵感" → 社区
    if any(w in combined for w in ["社区", "别人", "热门", "灵感", "推荐", "流行", "trending"]):
        sources.append(SearchSource.COMMUNITY)

    # 如果提到"网上"、"最新"、"参考"、网站名 → 联网搜索
    if any(w in combined for w in ["网上", "最新", "网络", "百度", "google", "参考", "真实"]):
        sources.append(SearchSource.DOUBAO_WEB)

    # RAG 在大部分创作场景下都有用
    if result.creative_intent != CreativeIntent.GENERAL:
        sources.append(SearchSource.RAG)

    # 如果没有明确的源，默认搜索社区 + RAG
    if not sources:
        sources = [SearchSource.COMMUNITY, SearchSource.RAG]

    result.search_sources = list(dict.fromkeys(sources))  # 去重保序
    result.reasoning = (
        f"识别到创作意图: {result.creative_intent.value}，"
        f"将从 {', '.join(s.value for s in result.search_sources)} 搜索参考素材"
    )

    return result
