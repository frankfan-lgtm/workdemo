"""
豆包联网搜索数据源
通过火山方舟 Responses API 内置的 web_search 工具进行联网搜索
API 不可用时降级到模拟数据
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class WebSearchResult:
    title: str
    url: str
    snippet: str
    image_url: str = ""
    source: str = "doubao_web"


# ============================================================
# 真实联网搜索（火山方舟 Responses API + web_search 工具）
# ============================================================

async def _search_web_llm(query: str, intent: str = "通用") -> Optional[List[WebSearchResult]]:
    """
    通过火山方舟 Responses API 的内置 web_search 工具进行联网搜索
    返回 None 表示调用失败
    """
    from agent.llm import chat_completion, extract_text_from_response, ARK_API_KEY

    if not ARK_API_KEY:
        return None

    search_prompt = (
        f"我正在进行{intent}方向的AI图像创作，需要搜索参考素材。"
        f"请搜索：{query}\n"
        f"找到相关的图片素材、设计趋势、教程或灵感参考。"
        f"对每个结果，请给出标题、链接和简短描述。"
    )

    messages = [
        {
            "role": "user",
            "content": [{"type": "input_text", "text": search_prompt}],
        },
    ]
    tools = [{"type": "web_search", "max_keyword": 3}]

    try:
        resp = await chat_completion(messages, tools=tools, temperature=0.3)
        text = extract_text_from_response(resp)
        if not text:
            return None

        # 解析 LLM 返回的文本，提取搜索结果
        results = _parse_web_results(text)
        return results if results else None

    except Exception as e:
        logger.warning(f"联网搜索失败: {e}")
        return None


def _parse_web_results(text: str) -> list[WebSearchResult]:
    """从 LLM 联网搜索的文本回复中提取结构化结果"""
    results = []

    # 尝试按段落分割，每段作为一个结果
    # 匹配常见格式：标题 + URL + 描述
    url_pattern = re.compile(r'https?://[^\s\)）\]]+')
    paragraphs = re.split(r'\n\n+|\n(?=\d+[\.\、])', text)

    for para in paragraphs:
        para = para.strip()
        if not para or len(para) < 10:
            continue

        urls = url_pattern.findall(para)
        url = urls[0] if urls else ""

        # 提取标题（第一行或加粗文字）
        lines = para.split('\n')
        title_line = lines[0].strip()
        # 清理 markdown 格式
        title = re.sub(r'[\*\#\d+\.\、\[\]]+', '', title_line).strip()
        if not title:
            continue

        # 剩余文字作为描述
        snippet = ' '.join(lines[1:]).strip() if len(lines) > 1 else para
        snippet = re.sub(r'https?://[^\s]+', '', snippet).strip()
        snippet = snippet[:200]

        if title:
            results.append(WebSearchResult(
                title=title[:100],
                url=url,
                snippet=snippet,
                image_url=f"https://picsum.photos/seed/{hash(title) % 10000}/400/400",
            ))

    return results[:6]  # 最多返回6条


# ============================================================
# 模拟数据（兜底）
# ============================================================

MOCK_WEB_RESULTS = {
    "电商": [
        WebSearchResult(
            title="2026春夏电商产品摄影趋势",
            url="https://example.com/ecommerce-trend-2026",
            snippet="柔和自然光 + 极简背景成为主流，强调产品质感与生活场景融合",
            image_url="https://picsum.photos/seed/ecom1/400/400",
        ),
        WebSearchResult(
            title="高转化率产品图拍摄技巧",
            url="https://example.com/product-photo-tips",
            snippet="45度俯拍角度、道具搭配、色彩心理学在电商摄影中的应用",
            image_url="https://picsum.photos/seed/ecom2/400/400",
        ),
        WebSearchResult(
            title="AI生成电商白底图最佳实践",
            url="https://example.com/ai-product-photo",
            snippet="使用AI工具快速生成高质量白底产品图，节省80%修图时间",
            image_url="https://picsum.photos/seed/ecom3/400/400",
        ),
    ],
    "流量照片": [
        WebSearchResult(
            title="小红书爆款图片风格解析",
            url="https://example.com/xiaohongshu-style",
            snippet="2026年小红书最火的5种图片风格：治愈系、复古胶片、氛围感写真...",
            image_url="https://picsum.photos/seed/trend1/400/400",
        ),
        WebSearchResult(
            title="INS网红照片调色教程",
            url="https://example.com/ins-color-grading",
            snippet="低饱和度、高质感的Instagram风格调色参数分享",
            image_url="https://picsum.photos/seed/trend2/400/400",
        ),
    ],
    "艺术创作": [
        WebSearchResult(
            title="2026数字艺术创作趋势报告",
            url="https://example.com/digital-art-2026",
            snippet="AI辅助创作成主流，混合媒介、3D渲染风格持续走高",
            image_url="https://picsum.photos/seed/art1/400/400",
        ),
        WebSearchResult(
            title="概念艺术大师作品集锦",
            url="https://example.com/concept-art-masters",
            snippet="Artstation年度最佳概念艺术作品合集",
            image_url="https://picsum.photos/seed/art2/400/400",
        ),
    ],
    "品牌设计": [
        WebSearchResult(
            title="极简品牌设计趋势",
            url="https://example.com/brand-minimal",
            snippet="去繁就简，2026品牌视觉设计趋势：几何图形、渐变色、动态logo",
            image_url="https://picsum.photos/seed/brand1/400/400",
        ),
        WebSearchResult(
            title="AI品牌设计工具对比评测",
            url="https://example.com/ai-brand-tools",
            snippet="Midjourney vs DALL-E vs 即梦：品牌设计场景下的AI工具横评",
            image_url="https://picsum.photos/seed/brand2/400/400",
        ),
    ],
    "影视": [
        WebSearchResult(
            title="电影概念设计流程揭秘",
            url="https://example.com/film-concept",
            snippet="从剧本到视觉：好莱坞概念设计师的完整工作流程",
            image_url="https://picsum.photos/seed/film1/400/400",
        ),
        WebSearchResult(
            title="AI在影视前期制作中的应用",
            url="https://example.com/ai-film-preproduction",
            snippet="用AI快速生成分镜、场景概念图、角色设定",
            image_url="https://picsum.photos/seed/film2/400/400",
        ),
    ],
    "通用": [
        WebSearchResult(
            title="AI图像生成Prompt技巧大全",
            url="https://example.com/prompt-guide",
            snippet="掌握这些prompt技巧，让AI生成更精准的图像",
            image_url="https://picsum.photos/seed/gen1/400/400",
        ),
        WebSearchResult(
            title="2026视觉设计趋势预测",
            url="https://example.com/design-trend-2026",
            snippet="色彩、构图、风格：今年最值得关注的视觉趋势",
            image_url="https://picsum.photos/seed/gen2/400/400",
        ),
    ],
}


def _search_web_mock(query: str, intent: str = "通用") -> list[WebSearchResult]:
    """模拟搜索兜底"""
    results = MOCK_WEB_RESULTS.get(intent, MOCK_WEB_RESULTS["通用"])
    filtered = [r for r in results if any(
        kw in r.title or kw in r.snippet
        for kw in query.replace("，", " ").replace(",", " ").split()
    )]
    return filtered if filtered else results


# ============================================================
# 统一入口
# ============================================================

async def search_web(query: str, intent: str = "通用") -> list[WebSearchResult]:
    """联网搜索：优先真实API，失败降级到模拟数据"""
    results = await _search_web_llm(query, intent)
    if results:
        return results
    return _search_web_mock(query, intent)
