"""
豆包联网搜索数据源
通过 MCP 协议调用豆包的联网搜索能力，支持文搜文、文搜图、图搜图
Demo 版本使用模拟数据，生产环境替换为真实 MCP 调用
"""

from dataclasses import dataclass


@dataclass
class WebSearchResult:
    title: str
    url: str
    snippet: str
    image_url: str = ""
    source: str = "doubao_web"


# 模拟的联网搜索结果
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


async def search_web(query: str, intent: str = "通用") -> list[WebSearchResult]:
    """
    豆包联网搜索
    Demo: 返回模拟数据
    生产环境: 通过 MCP 协议调用豆包联网搜索 API

    MCP 接入方式（生产环境）:
    1. 安装: pip install volcenginesdkarkruntime
    2. 配置 ARK_API_KEY 环境变量
    3. 通过 Streamable HTTP 连接豆包 MCP Server
       endpoint: https://mcp.doubao.com/sse (示例)
    4. 调用 tools/call: web_search, image_search 等工具
    """
    results = MOCK_WEB_RESULTS.get(intent, MOCK_WEB_RESULTS["通用"])
    # 根据 query 做简单的相关性过滤（demo简化版）
    filtered = [r for r in results if any(
        kw in r.title or kw in r.snippet
        for kw in query.replace("，", " ").replace(",", " ").split()
    )]
    return filtered if filtered else results
