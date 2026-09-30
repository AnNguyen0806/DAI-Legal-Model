const API_BASE =
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1"
    ? "http://localhost:8000"
    : "https://api.donghai.uk";

const API_URL = `${API_BASE}/api/v1/chat/completions`;
const HISTORY_URL = `${API_BASE}/api/v1/chat/history`;

async function readError(response) {
  try {
    const data = await response.json();
    return data.detail || data.message || response.statusText;
  } catch {
    return response.statusText;
  }
}

export async function askAI(prompt, allowExternal = false) {
  const response = await fetch(API_URL, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      allow_external: Boolean(allowExternal),
    }),
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  if (!response.body) {
    throw new Error("Core API không trả về response stream.");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let answer = "";
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();

    if (done) {
      break;
    }

    buffer += decoder.decode(value, { stream: true });

    const events = buffer.split("\n\n");
    buffer = events.pop() || "";

    for (const event of events) {
      const lines = event.split("\n");

      for (const line of lines) {
        if (!line.startsWith("data:")) {
          continue;
        }

        const raw = line.slice(5).trim();

        if (!raw) {
          continue;
        }

        try {
          const data = JSON.parse(raw);

          if (typeof data.delta === "string") {
            answer += data.delta;
          }
        } catch {
          // Bỏ qua data SSE không phải JSON.
        }
      }
    }
  }

  if (buffer.trim()) {
    for (const line of buffer.split("\n")) {
      if (!line.startsWith("data:")) {
        continue;
      }

      const raw = line.slice(5).trim();

      if (!raw) {
        continue;
      }

      try {
        const data = JSON.parse(raw);

        if (typeof data.delta === "string") {
          answer += data.delta;
        }
      } catch {
        // Ignore malformed trailing SSE data.
      }
    }
  }

  return answer.trim();
}

export async function getChatHistory(limit = 100) {
  const response = await fetch(
    `${HISTORY_URL}?limit=${encodeURIComponent(limit)}`,
    {
      method: "GET",
      credentials: "include",
    }
  );

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return await response.json();
}

export async function clearChatHistory() {
  const response = await fetch(HISTORY_URL, {
    method: "DELETE",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await readError(response));
  }

  return await response.json();
}