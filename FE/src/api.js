export async function askAI(message) {
  const response = await fetch(
    "https://api.donghai.uk/api/v1/chat/completions",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: "frontend-session",
        prompt: message,
      }),
    }
  );

  if (!response.ok) {
    throw new Error(`Core API lỗi: ${response.status}`);
  }

  const text = await response.text();

  console.log("RAW CORE RESPONSE:", text);

  let answer = "";

  const lines = text.split(/\r?\n/);

  for (const line of lines) {
    if (!line.startsWith("data:")) {
      continue;
    }

    const jsonText = line.substring(5).trim();

    try {
      const data = JSON.parse(jsonText);

      if (data.delta) {
        answer += data.delta;
      }
    } catch (error) {
      console.log("Không phải JSON:", jsonText);
    }
  }

  console.log("PARSED ANSWER:", answer);

  return answer.trim() || "AI không trả về câu trả lời.";
}