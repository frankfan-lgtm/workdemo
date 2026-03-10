"""
意图识别模块
根据用户输入判断：1) 是否需要搜索 2) 应该搜索哪些源 3) 搜索意图分类
支持两种模式：LLM（火山方舟 deepseek-v3）和规则兜底
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


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
    search_sources: List[SearchSource] = field(default_factory=list)
    search_query: str = ""
    reasoning: str = ""


# ============================================================
# LLM 意图识别（主路径）
# ============================================================

INTENT_SYSTEM_PROMPT = """你是即梦AI创作助手的意图分析模块。你的任务是分析用户的创作需求，判断是否需要搜索参考素材，以及应该从哪些数据源搜索。

## 输出格式
严格输出 JSON，不要包含任何其他文字：
```json
{
  "need_search": true,
  "creative_intent": "电商",
  "search_sources": ["community", "rag"],
  "search_query": "优化后的搜索关键词",
  "reasoning": "一句话解释你的判断理由"
}
```

## 字段说明

### need_search (bool)
- true: 用户需要搜索参考素材/灵感
- false: 用户明确要直接生成图片，不需要参考（如"帮我生成一只猫"）

### creative_intent (string)
从以下类别选一个最匹配的：
- "电商": 电商产品图、商品展示、详情页、白底图
- "流量照片": 小红书/INS风格、网红照、写真、穿搭、头像壁纸
- "艺术创作": 插画、油画、CG、二次元、动漫、国风、赛博朋克
- "品牌设计": logo、海报、banner、包装、VI设计
- "影视": 电影概念图、分镜、场景设计、特效
- "通用": 不属于以上任何类别

### search_sources (string[])
从以下数据源中选择1-4个最合适的，按优先级排序：
- "doubao_web": 联网搜索 — 用户需要最新资讯、真实参考图、网络趋势时使用
- "rag": 优质素材库 — 高质量标注数据，适合需要专业参考的创作场景
- "user_assets": 用户资产 — 用户提到"我的""之前""上次"等个人素材时使用
- "community": 社区灵感 — 其他创作者发布的作品，适合找灵感、看热门

### search_query (string)
根据用户输入提炼出更适合搜索的关键词，去掉口语化表达，保留核心创作意图。

## 判断策略
1. 如果用户明确说"生成/画/创建"且没有提到"参考/找/搜索/灵感"，则 need_search=false
2. 如果用户想找参考、灵感、类似风格，则 need_search=true
3. 联网搜索(doubao_web)适合：需要最新趋势、真实世界参考、具体品牌/IP参考
4. RAG库适合：专业创作场景，需要高质量标注素材
5. 用户资产适合：用户明确提到个人历史素材
6. 社区灵感适合：找灵感、看别人怎么做、热门作品"""


async def analyze_intent_llm(user_input: str, context: str = "") -> Optional[IntentResult]:
    """
    使用火山方舟 LLM 进行意图识别
    返回 None 表示 LLM 调用失败，应降级到规则引擎
    """
    from agent.llm import chat_completion, extract_json_from_response

    messages = [
        {
            "role": "system",
            "content": [{"type": "input_text", "text": INTENT_SYSTEM_PROMPT}],
        },
        {
            "role": "user",
            "content": [{"type": "input_text", "text": user_input}],
        },
    ]

    if context:
        messages[1]["content"].append(
            {"type": "input_text", "text": f"\n\n上下文信息：{context}"}
        )

    try:
        resp = await chat_completion(messages, temperature=0.1)
        data = extract_json_from_response(resp)
        if not data:
            logger.warning("LLM 返回的内容无法解析为 JSON")
            return None

        # 解析 creative_intent
        intent_map = {v.value: v for v in CreativeIntent}
        creative_intent = intent_map.get(
            data.get("creative_intent", "通用"), CreativeIntent.GENERAL
        )

        # 解析 search_sources
        source_map = {v.value: v for v in SearchSource}
        search_sources = []
        for s in data.get("search_sources", []):
            if s in source_map:
                search_sources.append(source_map[s])

        return IntentResult(
            need_search=data.get("need_search", True),
            creative_intent=creative_intent,
            search_sources=search_sources,
            search_query=data.get("search_query", user_input),
            reasoning=data.get("reasoning", ""),
        )
    except Exception as e:
        logger.warning(f"LLM 意图识别失败，降级到规则引擎: {e}")
        return None


# ============================================================
# 规则引擎意图识别（兜底）
# ============================================================

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

SEARCH_TRIGGER_WORDS = [
    "参考", "搜索", "找", "类似", "风格", "灵感", "借鉴",
    "像", "看看", "有没有", "推荐", "想要", "帮我找",
    "trending", "最新", "流行", "热门", "同款", "模仿",
]

NO_SEARCH_WORDS = [
    "生成一", "画一", "创建一", "做一个", "帮我画", "帮我生成",
]


def analyze_intent_rules(user_input: str, context: str = "") -> IntentResult:
    """基于规则 + 关键词的意图分析（兜底方案）"""
    combined = f"{user_input} {context}".lower()
    result = IntentResult()
    result.search_query = user_input

    has_search_trigger = any(w in combined for w in SEARCH_TRIGGER_WORDS)
    has_no_search = any(w in combined for w in NO_SEARCH_WORDS)

    if has_no_search and not has_search_trigger:
        result.need_search = False
        result.reasoning = "用户意图为直接生成，无需搜索参考素材"
        return result

    result.need_search = True

    intent_scores: Dict[CreativeIntent, int] = {}
    for intent, keywords in INTENT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in combined)
        if score > 0:
            intent_scores[intent] = score

    if intent_scores:
        result.creative_intent = max(intent_scores, key=intent_scores.get)
    else:
        result.creative_intent = CreativeIntent.GENERAL

    sources = []
    if any(w in combined for w in ["我的", "之前", "上次", "我生成", "我收藏", "我下载"]):
        sources.append(SearchSource.USER_ASSETS)
    if any(w in combined for w in ["社区", "别人", "热门", "灵感", "推荐", "流行", "trending"]):
        sources.append(SearchSource.COMMUNITY)
    if any(w in combined for w in ["网上", "最新", "网络", "百度", "google", "参考", "真实"]):
        sources.append(SearchSource.DOUBAO_WEB)
    if result.creative_intent != CreativeIntent.GENERAL:
        sources.append(SearchSource.RAG)
    if not sources:
        sources = [SearchSource.COMMUNITY, SearchSource.RAG]

    result.search_sources = list(dict.fromkeys(sources))
    result.reasoning = (
        f"识别到创作意图: {result.creative_intent.value}，"
        f"将从 {', '.join(s.value for s in result.search_sources)} 搜索参考素材"
    )
    return result


# ============================================================
# 统一入口：LLM 优先，规则兜底
# ============================================================

async def analyze_intent(user_input: str, context: str = "") -> IntentResult:
    """
    意图识别统一入口
    优先使用 LLM（火山方舟 deepseek-v3），失败时降级到规则引擎
    """
    from agent.llm import ARK_API_KEY

    # 如果配置了 API Key，优先用 LLM
    if ARK_API_KEY:
        result = await analyze_intent_llm(user_input, context)
        if result is not None:
            return result

    # 降级到规则引擎
    return analyze_intent_rules(user_input, context)
