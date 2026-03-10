// === 即梦 AI 创作助手 前端逻辑 ===

const chatArea = document.getElementById("chatArea");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

let isProcessing = false;

// 颜色映射
const SOURCE_COLORS = {
  doubao_web: "#6366f1",
  rag: "#f59e0b",
  user_assets: "#10b981",
  community: "#ec4899",
};

const SOURCE_LABELS = {
  doubao_web: "联网搜索",
  rag: "优质素材库",
  user_assets: "我的资产",
  community: "社区灵感",
};

// 自动调整文本框高度
userInput.addEventListener("input", function () {
  this.style.height = "auto";
  this.style.height = Math.min(this.scrollHeight, 120) + "px";
});

function handleKeyDown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendQuickPrompt(btn) {
  userInput.value = btn.textContent;
  sendMessage();
}

async function sendMessage() {
  const text = userInput.value.trim();
  if (!text || isProcessing) return;

  isProcessing = true;
  sendBtn.disabled = true;

  // 清除欢迎页
  const welcome = chatArea.querySelector(".welcome-message");
  if (welcome) welcome.remove();

  // 添加用户消息
  appendUserMessage(text);
  userInput.value = "";
  userInput.style.height = "auto";

  // 显示搜索中状态
  const loadingEl = appendSearchingIndicator();

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    const data = await resp.json();
    loadingEl.remove();

    if (data.need_search) {
      appendIntentCard(data.intent);
      appendSearchResults(data.results_by_source, data.summary);
    } else {
      appendNoSearchMessage(data.reasoning);
    }
  } catch (err) {
    loadingEl.remove();
    appendNoSearchMessage("抱歉，请求出错了，请稍后再试。");
    console.error(err);
  }

  isProcessing = false;
  sendBtn.disabled = false;
  scrollToBottom();
}

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "message message-user";
  div.innerHTML = `<div class="message-content">${escapeHtml(text)}</div>`;
  chatArea.appendChild(div);
  scrollToBottom();
}

function appendSearchingIndicator() {
  const div = document.createElement("div");
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="agent-header">
      <div class="agent-avatar">✦</div>
      <span class="agent-name">即梦创作助手</span>
    </div>
    <div class="searching-indicator">
      <div class="searching-dots">
        <span></span><span></span><span></span>
      </div>
      <span>正在分析意图并搜索素材...</span>
    </div>
  `;
  chatArea.appendChild(div);
  scrollToBottom();
  return div;
}

function appendIntentCard(intent) {
  const badgeColor =
    intent.creative_intent === "通用" ? "#6366f1" : SOURCE_COLORS.rag;
  const sourceTagsHtml = (intent.search_sources || [])
    .map(
      (s) =>
        `<span class="source-tag ${s}">${SOURCE_LABELS[s] || s}</span>`
    )
    .join("");

  const div = document.createElement("div");
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="agent-header">
      <div class="agent-avatar">✦</div>
      <span class="agent-name">即梦创作助手</span>
    </div>
    <div class="intent-card">
      <div class="intent-header">
        🔍 意图分析
        <span class="intent-badge" style="background:${badgeColor}22;color:${badgeColor}">${escapeHtml(intent.creative_intent)}</span>
      </div>
      <div class="intent-reasoning">${escapeHtml(intent.reasoning)}</div>
      <div class="search-sources-tags">${sourceTagsHtml}</div>
    </div>
  `;
  chatArea.appendChild(div);
}

function appendSearchResults(resultsBySource, summary) {
  let sectionsHtml = "";

  for (const [source, items] of Object.entries(resultsBySource)) {
    const color = SOURCE_COLORS[source] || "#6366f1";
    const label = SOURCE_LABELS[source] || source;

    const cardsHtml = items
      .map((item) => {
        let metaHtml = "";
        if (item.extra) {
          if (item.extra.author) {
            metaHtml = `<div class="result-card-meta">
              <span class="result-source-indicator" style="background:${color}"></span>
              ${escapeHtml(item.extra.author)} · ❤ ${item.extra.likes || 0}
            </div>`;
          } else if (item.extra.asset_type) {
            metaHtml = `<div class="result-card-meta">
              <span class="result-source-indicator" style="background:${color}"></span>
              ${escapeHtml(item.extra.asset_type)} · ${item.extra.created_at || ""}
            </div>`;
          } else if (item.extra.quality_score) {
            metaHtml = `<div class="result-card-meta">
              <span class="result-source-indicator" style="background:${color}"></span>
              质量分: ${(item.extra.quality_score * 100).toFixed(0)}
            </div>`;
          } else if (item.extra.url) {
            metaHtml = `<div class="result-card-meta">
              <span class="result-source-indicator" style="background:${color}"></span>
              网络来源
            </div>`;
          }
        }

        return `
          <div class="result-card">
            <img class="result-card-image" src="${escapeHtml(item.image_url)}" alt="${escapeHtml(item.title)}" loading="lazy">
            <div class="result-card-info">
              <div class="result-card-title">${escapeHtml(item.title)}</div>
              <div class="result-card-desc">${escapeHtml(item.description)}</div>
              ${metaHtml}
            </div>
          </div>
        `;
      })
      .join("");

    sectionsHtml += `
      <div class="source-section">
        <div class="source-section-header">
          <span class="source-section-dot" style="background:${color}"></span>
          ${escapeHtml(label)}
          <span style="color:var(--text-muted);font-weight:400">(${items.length})</span>
        </div>
        <div class="results-grid">${cardsHtml}</div>
      </div>
    `;
  }

  const div = document.createElement("div");
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="search-results">
      <div class="results-summary">${escapeHtml(summary)}</div>
      ${sectionsHtml}
    </div>
  `;
  chatArea.appendChild(div);
  scrollToBottom();
}

function appendNoSearchMessage(text) {
  const div = document.createElement("div");
  div.className = "message message-agent";
  div.innerHTML = `
    <div class="agent-header">
      <div class="agent-avatar">✦</div>
      <span class="agent-name">即梦创作助手</span>
    </div>
    <div class="no-search-message">${escapeHtml(text)}</div>
  `;
  chatArea.appendChild(div);
  scrollToBottom();
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    chatArea.scrollTop = chatArea.scrollHeight;
  });
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
