// ---------------------------------------------------------------------------
// Tab switching
// ---------------------------------------------------------------------------
const tabChat = document.getElementById("tab-chat");
const tabImage = document.getElementById("tab-image");
const chatPanel = document.getElementById("chat-panel");
const imagePanel = document.getElementById("image-panel");

tabChat.addEventListener("click", () => switchTab("chat"));
tabImage.addEventListener("click", () => switchTab("image"));

function switchTab(tab) {
  const isChat = tab === "chat";
  tabChat.classList.toggle("active", isChat);
  tabImage.classList.toggle("active", !isChat);
  chatPanel.classList.toggle("active", isChat);
  imagePanel.classList.toggle("active", !isChat);
}

// ---------------------------------------------------------------------------
// Chat
// ---------------------------------------------------------------------------
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatWindow = document.getElementById("chat-window");
const resetBtn = document.getElementById("reset-btn");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  chatInput.value = "";

  const loadingBubble = appendMessage("assistant", "Thinking...", true);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();

    if (data.error) {
      loadingBubble.textContent = `⚠️ ${data.error}`;
    } else {
      loadingBubble.textContent = data.reply;
    }
  } catch (err) {
    loadingBubble.textContent = "⚠️ Failed to reach the server.";
  }
});

resetBtn.addEventListener("click", async () => {
  await fetch("/api/reset", { method: "POST" });
  chatWindow.innerHTML = "";
  appendMessage("assistant", "Conversation cleared. Ask me anything!");
});

function appendMessage(role, text, returnBubble = false) {
  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}`;

  const bubble = document.createElement("span");
  bubble.className = "bubble";
  bubble.textContent = text;

  wrapper.appendChild(bubble);
  chatWindow.appendChild(wrapper);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  return returnBubble ? bubble : null;
}

// ---------------------------------------------------------------------------
// Image generation
// ---------------------------------------------------------------------------
const imageForm = document.getElementById("image-form");
const imageInput = document.getElementById("image-input");
const imageWindow = document.getElementById("image-window");

imageForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = imageInput.value.trim();
  if (!prompt) return;

  const placeholder = document.querySelector(".placeholder-text");
  if (placeholder) placeholder.remove();

  const loadingMsg = document.createElement("p");
  loadingMsg.className = "loading";
  loadingMsg.textContent = `Generating: "${prompt}"...`;
  imageWindow.appendChild(loadingMsg);

  try {
    const res = await fetch("/api/generate-image", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();

    loadingMsg.remove();

    if (data.error) {
      const errMsg = document.createElement("p");
      errMsg.className = "loading";
      errMsg.textContent = `⚠️ ${data.error}`;
      imageWindow.appendChild(errMsg);
    } else {
      const img = document.createElement("img");
      img.src = data.image;
      img.alt = prompt;
      imageWindow.appendChild(img);
    }
  } catch (err) {
    loadingMsg.textContent = "⚠️ Failed to reach the server.";
  }

  imageInput.value = "";
});
