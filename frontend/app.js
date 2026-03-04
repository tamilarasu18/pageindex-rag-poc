/**
 * PageIndex POC — Frontend Application Logic
 *
 * Handles: file upload, document list, tree visualization,
 * and Q&A chat with the FastAPI backend.
 */

const API_BASE = "http://localhost:8000/api";

// ─── State ───────────────────────────────────────────────────────────────────
let selectedDocId = null;
let pollingInterval = null;

// ─── DOM References ──────────────────────────────────────────────────────────
const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
const uploadProgress = document.getElementById("uploadProgress");
const uploadFill = document.getElementById("uploadFill");
const uploadText = document.getElementById("uploadText");
const docList = document.getElementById("docList");
const treeViewer = document.getElementById("treeViewer");
const treeInfo = document.getElementById("treeInfo");
const chatMessages = document.getElementById("chatMessages");
const chatInput = document.getElementById("chatInput");
const chatSend = document.getElementById("chatSend");
const chatHint = document.getElementById("chatHint");
const apiStatus = document.getElementById("apiStatus");

// ─── Init ────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  loadDocuments();
  setupUpload();
  setupChat();
  // Poll for document status updates every 5 seconds
  pollingInterval = setInterval(loadDocuments, 5000);
});

// ─── Health Check ────────────────────────────────────────────────────────────
async function checkHealth() {
  const dot = apiStatus.querySelector(".status-dot");
  const text = apiStatus.querySelector(".status-text");
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    dot.className = "status-dot connected";
    text.textContent = data.groq_configured ? "Connected" : "No API Key";
  } catch {
    dot.className = "status-dot error";
    text.textContent = "Backend offline";
  }
}

// ─── Upload ──────────────────────────────────────────────────────────────────
function setupUpload() {
  uploadZone.addEventListener("click", () => fileInput.click());
  fileInput.addEventListener("change", handleFileSelect);

  // Drag & drop
  uploadZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    uploadZone.classList.add("dragover");
  });
  uploadZone.addEventListener("dragleave", () => {
    uploadZone.classList.remove("dragover");
  });
  uploadZone.addEventListener("drop", (e) => {
    e.preventDefault();
    uploadZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && file.name.toLowerCase().endsWith(".pdf")) {
      uploadFile(file);
    }
  });
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) uploadFile(file);
  fileInput.value = "";
}

async function uploadFile(file) {
  uploadProgress.style.display = "block";
  uploadFill.style.width = "30%";
  uploadText.textContent = `Uploading ${file.name}...`;

  try {
    const formData = new FormData();
    formData.append("file", file);

    uploadFill.style.width = "60%";

    const res = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Upload failed");
    }

    const data = await res.json();
    uploadFill.style.width = "100%";
    uploadText.textContent = "✅ Uploaded! Indexing in progress...";

    setTimeout(() => {
      uploadProgress.style.display = "none";
      uploadFill.style.width = "0%";
    }, 2000);

    loadDocuments();
    selectDocument(data.document.id);
  } catch (err) {
    uploadFill.style.width = "100%";
    uploadFill.style.background = "var(--accent-red)";
    uploadText.textContent = `❌ ${err.message}`;
    setTimeout(() => {
      uploadProgress.style.display = "none";
      uploadFill.style.width = "0%";
      uploadFill.style.background = "";
    }, 3000);
  }
}

// ─── Document List ───────────────────────────────────────────────────────────
async function loadDocuments() {
  try {
    const res = await fetch(`${API_BASE}/documents`);
    const data = await res.json();
    renderDocList(data.documents);

    // If selected doc just became ready, refresh tree
    if (selectedDocId) {
      const doc = data.documents.find((d) => d.id === selectedDocId);
      if (doc && doc.status === "ready") {
        loadTree(selectedDocId);
        enableChat();
      }
    }
  } catch {
    // Backend might not be running yet
  }
}

function renderDocList(documents) {
  if (!documents.length) {
    docList.innerHTML = `
            <div class="doc-list__empty">
                <p>No documents yet</p>
                <p class="doc-list__empty-hint">Upload a PDF to get started</p>
            </div>`;
    return;
  }

  docList.innerHTML = documents
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .map((doc) => {
      const statusClass = `doc-item__status--${doc.status}`;
      const statusLabel =
        {
          uploaded: "Uploaded",
          indexing: "Indexing...",
          ready: "Ready",
          error: "Error",
        }[doc.status] || doc.status;

      const isActive = doc.id === selectedDocId;

      return `
            <div class="doc-item ${isActive ? "active" : ""}"
                 onclick="selectDocument('${doc.id}')">
                <div class="doc-item__icon">📄</div>
                <div class="doc-item__info">
                    <div class="doc-item__name" title="${doc.filename}">${doc.filename}</div>
                    <div class="doc-item__meta">${doc.page_count || "?"} pages</div>
                </div>
                <span class="doc-item__status ${statusClass}">${statusLabel}</span>
                <button class="doc-item__delete"
                        onclick="event.stopPropagation(); deleteDocument('${doc.id}')"
                        title="Delete">🗑</button>
            </div>`;
    })
    .join("");
}

async function selectDocument(docId) {
  selectedDocId = docId;
  loadDocuments(); // re-render with active state

  // Check if ready
  try {
    const res = await fetch(`${API_BASE}/documents/${docId}`);
    const data = await res.json();
    const doc = data.document;

    if (doc.status === "ready") {
      loadTree(docId);
      enableChat();
    } else if (doc.status === "indexing") {
      treeViewer.innerHTML = `
                <div class="tree-viewer__empty">
                    <div class="tree-viewer__empty-icon" style="animation: pulse 2s infinite">⏳</div>
                    <p>Indexing in progress...</p>
                    <p class="tree-viewer__empty-hint">
                        The LLM is analyzing your document and building<br>
                        a hierarchical tree structure. This may take a few minutes.
                    </p>
                </div>`;
      disableChat("Document is being indexed...");
    } else if (doc.status === "error") {
      treeViewer.innerHTML = `
                <div class="tree-viewer__empty">
                    <div class="tree-viewer__empty-icon">❌</div>
                    <p>Indexing failed</p>
                    <p class="tree-viewer__empty-hint">${doc.error || "Unknown error"}</p>
                </div>`;
      disableChat("Indexing failed");
    } else {
      treeViewer.innerHTML = `
                <div class="tree-viewer__empty">
                    <div class="tree-viewer__empty-icon">📄</div>
                    <p>Document uploaded</p>
                    <p class="tree-viewer__empty-hint">Waiting for indexing to start...</p>
                </div>`;
      disableChat("Waiting for indexing...");
    }
  } catch {
    // ignore
  }
}

async function deleteDocument(docId) {
  if (!confirm("Delete this document?")) return;
  try {
    await fetch(`${API_BASE}/documents/${docId}`, { method: "DELETE" });
    if (selectedDocId === docId) {
      selectedDocId = null;
      resetTreeViewer();
      resetChat();
    }
    loadDocuments();
  } catch {
    // ignore
  }
}

// ─── Tree Viewer ─────────────────────────────────────────────────────────────
async function loadTree(docId) {
  try {
    const res = await fetch(`${API_BASE}/documents/${docId}/tree`);
    if (!res.ok) return;
    const data = await res.json();

    const tree = data.tree;
    const treeData = tree.tree || tree;
    const title = tree.title || "Document";
    const pageCount = tree.page_count || "?";

    treeInfo.textContent = `${title} · ${pageCount} pages`;
    treeViewer.innerHTML = renderTree(treeData);
  } catch {
    treeViewer.innerHTML = `
            <div class="tree-viewer__empty">
                <div class="tree-viewer__empty-icon">⚠️</div>
                <p>Failed to load tree</p>
            </div>`;
  }
}

function renderTree(nodes, depth = 0) {
  if (!Array.isArray(nodes)) nodes = [nodes];

  return nodes
    .map((node) => {
      const hasChildren = node.nodes && node.nodes.length > 0;
      const startPage = node.start_page || node.start_index || "?";
      const endPage = node.end_page || node.end_index || "?";
      const icon = hasChildren ? "📁" : "📄";
      const nodeId = node.node_id || "";
      const summary = node.summary || "";

      let childrenHtml = "";
      if (hasChildren) {
        childrenHtml = `
                    <div class="tree-node__children" id="children-${nodeId}">
                        ${renderTree(node.nodes, depth + 1)}
                    </div>`;
      }

      return `
            <div class="tree-node">
                <div class="tree-node__header" onclick="toggleNode('${nodeId}')">
                    <span class="tree-node__toggle ${hasChildren ? "" : "empty"}"
                          id="toggle-${nodeId}">
                        ${hasChildren ? "▶" : "·"}
                    </span>
                    <span class="tree-node__icon">${icon}</span>
                    <span class="tree-node__title">${node.title || "Untitled"}</span>
                    <span class="tree-node__pages">p.${startPage}–${endPage}</span>
                </div>
                ${summary ? `<div class="tree-node__summary">${summary}</div>` : ""}
                ${childrenHtml}
            </div>`;
    })
    .join("");
}

function toggleNode(nodeId) {
  const children = document.getElementById(`children-${nodeId}`);
  const toggle = document.getElementById(`toggle-${nodeId}`);
  if (!children) return;

  const isExpanded = children.classList.contains("expanded");
  children.classList.toggle("expanded");
  toggle.classList.toggle("expanded");
}

function resetTreeViewer() {
  treeInfo.textContent = "";
  treeViewer.innerHTML = `
        <div class="tree-viewer__empty">
            <div class="tree-viewer__empty-icon">🌳</div>
            <p>Select a document to view its index tree</p>
            <p class="tree-viewer__empty-hint">
                PageIndex creates a hierarchical structure<br>
                like a "Table of Contents" optimized for LLMs
            </p>
        </div>`;
}

// ─── Chat ────────────────────────────────────────────────────────────────────
function setupChat() {
  chatSend.addEventListener("click", sendMessage);
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

function enableChat() {
  chatInput.disabled = false;
  chatSend.disabled = false;
  chatHint.textContent = "Press Enter to send · Reasoning-based retrieval";
}

function disableChat(hint) {
  chatInput.disabled = true;
  chatSend.disabled = true;
  chatHint.textContent = hint || "Upload and index a document first";
}

function resetChat() {
  chatMessages.innerHTML = `
        <div class="chat__welcome">
            <div class="chat__welcome-icon">🧠</div>
            <h3>Reasoning-based Retrieval</h3>
            <p>
                Ask any question about your uploaded document.
                PageIndex uses LLM reasoning to navigate the tree
                structure and find the most relevant sections.
            </p>
            <div class="chat__features">
                <div class="chat__feature"><span>🎯</span> No vector similarity</div>
                <div class="chat__feature"><span>🧩</span> No chunking</div>
                <div class="chat__feature"><span>🔍</span> Human-like search</div>
            </div>
        </div>`;
  disableChat();
}

async function sendMessage() {
  const question = chatInput.value.trim();
  if (!question || !selectedDocId) return;

  // Clear welcome if first message
  const welcome = chatMessages.querySelector(".chat__welcome");
  if (welcome) welcome.remove();

  // Add user message
  appendMessage("user", question);
  chatInput.value = "";

  // Add loading indicator
  const loadingId = appendLoading();

  // Disable input while waiting
  chatInput.disabled = true;
  chatSend.disabled = true;

  try {
    const res = await fetch(`${API_BASE}/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_id: selectedDocId,
        question: question,
      }),
    });

    removeLoading(loadingId);

    if (!res.ok) {
      const err = await res.json();
      appendMessage("assistant", `⚠️ ${err.detail || "Query failed"}`);
    } else {
      const data = await res.json();
      appendAnswer(data);
    }
  } catch (err) {
    removeLoading(loadingId);
    appendMessage("assistant", `⚠️ Connection error: ${err.message}`);
  }

  chatInput.disabled = false;
  chatSend.disabled = false;
  chatInput.focus();
}

function appendMessage(role, text) {
  const div = document.createElement("div");
  div.className = `chat-msg chat-msg--${role}`;
  const avatar = role === "user" ? "👤" : "🧠";
  div.innerHTML = `
        <div class="chat-msg__avatar">${avatar}</div>
        <div class="chat-msg__bubble">${escapeHtml(text)}</div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendAnswer(data) {
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg--assistant";

  let sourcesHtml = "";
  if (data.sources && data.sources.length) {
    sourcesHtml = `
            <div class="chat-msg__sources">
                <div class="chat-msg__sources-title">📎 Sources</div>
                ${data.sources
                  .map(
                    (s) =>
                      `<div class="chat-msg__source">📄 ${s.title} (pages ${s.start_page}–${s.end_page})</div>`,
                  )
                  .join("")}
            </div>`;
  }

  let reasoningHtml = "";
  if (data.reasoning) {
    const reasonId = `reasoning-${Date.now()}`;
    reasoningHtml = `
            <div class="chat-msg__reasoning" onclick="toggleReasoning('${reasonId}')">
                <div class="chat-msg__reasoning-toggle">🔍 View reasoning process</div>
                <div class="chat-msg__reasoning-content" id="${reasonId}">
                    ${escapeHtml(data.reasoning)}
                </div>
            </div>`;
  }

  div.innerHTML = `
        <div class="chat-msg__avatar">🧠</div>
        <div class="chat-msg__bubble">
            ${formatAnswer(data.answer)}
            ${sourcesHtml}
            ${reasoningHtml}
        </div>`;

  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function appendLoading() {
  const id = `loading-${Date.now()}`;
  const div = document.createElement("div");
  div.className = "chat-msg chat-msg--assistant chat-msg--loading";
  div.id = id;
  div.innerHTML = `
        <div class="chat-msg__avatar">🧠</div>
        <div class="chat-msg__bubble">
            <span>Thinking</span>
            <div class="loading-dots">
                <span></span><span></span><span></span>
            </div>
        </div>`;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return id;
}

function removeLoading(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function toggleReasoning(id) {
  const el = document.getElementById(id);
  if (el) el.classList.toggle("expanded");
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function formatAnswer(text) {
  // Basic markdown-like formatting
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>")
    .replace(/\n/g, "<br>");
}

function closeModal() {
  document.getElementById("flowModal").style.display = "none";
}
