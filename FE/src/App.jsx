import { useEffect, useRef, useState } from "react";
import {
  Scale,
  MessageCircle,
  Send,
  Sparkles,
  ShieldCheck,
  Search,
  ArrowRight,
  Trash2,
  RefreshCw,
} from "lucide-react";
import {
  askAI,
  getChatHistory,
  clearChatHistory,
} from "./api";

function App() {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);

  // Danh sach cau hoi goi y. Moi lan tai lai se lay ngau nhien 3 cau.
  const SUGGESTIONS = [
    "Đăng ký tạm trú cần những giấy tờ gì?",
    "Đăng ký tạm trú có mất phí không?",
    "Đăng ký kết hôn cần những giấy tờ gì?",
    "Đăng ký khai sinh cần những giấy tờ gì?",
    "Làm căn cước công dân cần những giấy tờ gì?",
    "Cấp hộ chiếu phổ thông cần thủ tục gì?",
    "Đăng ký thường trú cần những giấy tờ gì?",
    "Xin cấp giấy phép lái xe cần điều kiện gì?",
    "Chứng thực chữ ký cần những giấy tờ gì?",
    "Cấp phiếu lý lịch tư pháp cần làm thế nào?",
    "Đăng ký hộ kinh doanh cần những giấy tờ gì?",
    "Thủ tục thay đổi thông tin cư trú như thế nào?",
    "Đăng ký khai tử cần những giấy tờ gì?",
    "Cấp lại căn cước công dân mất bao lâu?",
    "Đăng ký xe cần những giấy tờ gì?",
    "Cấp giấy chứng nhận quyền sử dụng đất cần thủ tục gì?",
    "Đổi giấy phép lái xe cần những giấy tờ gì?",
    "Xin xác nhận tình trạng hôn nhân cần làm thế nào?",
  ];

  const getRandomSuggestions = () => {
    const shuffled = [...SUGGESTIONS];

    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }

    return shuffled.slice(0, 3);
  };

  const [quickQuestions, setQuickQuestions] = useState(() => getRandomSuggestions());

  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

  const loadHistory = async () => {
    try {
      setHistoryLoading(true);
      const result = await getChatHistory();

      if (result.success) {
        setHistory(result.messages || []);
      }
    } catch (error) {
      console.error("HISTORY ERROR:", error);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [history, loading]);

  const handleAskAI = async () => {
    const currentQuestion = question.trim();

    if (!currentQuestion || loading) return;

    setQuestion("");
    setLoading(true);

    const userMessageId = `local-user-${Date.now()}`;
    const loadingMessageId = `local-ai-${Date.now()}`;

    setHistory((prev) => [
      ...prev,
      {
        id: userMessageId,
        role: "user",
        content: currentQuestion,
      },
      {
        id: loadingMessageId,
        role: "assistant",
        content: "",
        isLoading: true,
      },
    ]);

    try {
      await askAI(currentQuestion);
      await loadHistory();
    } catch (error) {
      console.error("AI ERROR:", error);
      alert("Lỗi kết nối Core API: " + error.message);
    } finally {
      setLoading(false);
      setQuickQuestions(getRandomSuggestions());
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAskAI();
    }
  };

  const handleQuickQuestion = (item) => {
    setQuestion(item);
    inputRef.current?.focus();
  };

  const handleClearHistory = async () => {
    if (!window.confirm("Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện này?")) {
      return;
    }

    try {
      await clearChatHistory();
      setHistory([]);
      setQuickQuestions(getRandomSuggestions());
      setQuestion("");
    } catch (error) {
      console.error("CLEAR HISTORY ERROR:", error);
      alert("Không thể xóa lịch sử chat.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 text-slate-900">

      {/* TOP BAR */}
      <div className="bg-[#061f42] text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-2 text-xs md:text-sm">
          <div className="flex items-center gap-2">
            <ShieldCheck size={15} />
            Cổng thông tin hỗ trợ pháp lý bằng AI
          </div>
          <div className="hidden text-slate-300 md:block">
            Hỗ trợ trực tuyến • AI Pháp Lý
          </div>
        </div>
      </div>

      {/* HEADER */}
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-[72px] max-w-6xl items-center justify-between px-5">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#062b5c] shadow-sm">
              <Scale size={24} className="text-[#f4c430]" />
            </div>

            <div>
              <div className="text-xl font-bold tracking-tight text-[#062b5c]">
                AI Pháp Lý
              </div>
              <div className="text-xs text-slate-500">
                Hỏi gì · Trả lời đó
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            AI đang hoạt động
          </div>
        </div>
      </header>

      {/* CHAT PAGE */}
      <main className="mx-auto max-w-5xl px-4 py-8 md:px-6">

        {/* TITLE */}
        <div className="mb-6 text-center">
          <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-semibold text-blue-700">
            <Sparkles size={16} />
            Trợ lý pháp lý thông minh
          </div>

          <h1 className="text-3xl font-extrabold tracking-tight text-[#062b5c] md:text-4xl">
            Giải đáp pháp luật bằng AI
          </h1>

          <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-slate-500 md:text-base">
            Tra cứu thủ tục hành chính và thông tin pháp luật bằng
            Local RAG, Qdrant, MCP và Qwen.
          </p>
        </div>

        {/* CHAT CONTAINER */}
        <section className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-2xl shadow-blue-100/50">

          {/* CHAT HEADER */}
          <div className="flex items-center justify-between border-b border-slate-200 bg-gradient-to-r from-[#062b5c] to-[#0b4389] px-5 py-4 text-white">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10">
                <MessageCircle size={20} />
              </div>

              <div>
                <div className="font-semibold">Chat với AI Pháp Lý</div>
                <div className="text-xs text-blue-100">
                  Cuộc trò chuyện được lưu theo phiên trình duyệt
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={loadHistory}
                disabled={historyLoading}
                title="Làm mới"
                className="rounded-xl bg-white/10 p-2 transition hover:bg-white/20 disabled:opacity-50"
              >
                <RefreshCw
                  size={17}
                  className={historyLoading ? "animate-spin" : ""}
                />
              </button>

              <button
                type="button"
                onClick={handleClearHistory}
                disabled={historyLoading || history.length === 0}
                title="Xóa cuộc trò chuyện"
                className="rounded-xl bg-white/10 p-2 transition hover:bg-red-500/30 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <Trash2 size={17} />
              </button>
            </div>
          </div>

          {/* MESSAGES */}
          <div className="h-[560px] overflow-y-auto bg-gradient-to-b from-white to-slate-50 px-4 py-6 md:px-8">
            {historyLoading ? (
              <div className="flex h-full items-center justify-center text-sm text-slate-400">
                Đang tải cuộc trò chuyện...
              </div>
            ) : history.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                  <Scale size={30} />
                </div>

                <h2 className="text-lg font-semibold text-[#062b5c]">
                  Xin chào! Tôi là AI Pháp Lý
                </h2>

                <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
                  Hãy đặt câu hỏi về thủ tục hành chính hoặc thông tin pháp luật.
                  Hệ thống sẽ ưu tiên tra cứu dữ liệu pháp lý nội bộ.
                </p>

                <div className="mt-6 flex flex-wrap justify-center gap-2">
                  {quickQuestions.map((item, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => handleQuickQuestion(item)}
                      className="group rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-600 shadow-sm transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                    >
                      {item}
                      <ArrowRight
                        size={14}
                        className="ml-2 inline-block opacity-0 transition group-hover:translate-x-1 group-hover:opacity-100"
                      />
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-3xl space-y-6">
                {history.map((item) => (
                  <div
                    key={item.id}
                    className={
                      item.role === "user"
                        ? "flex justify-end"
                        : "flex justify-start"
                    }
                  >
                    {item.role === "user" ? (
                      <div className="max-w-[82%] rounded-2xl rounded-br-md bg-blue-600 px-5 py-3.5 text-white shadow-sm">
                        <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-blue-100">
                          Bạn
                        </div>
                        <div className="whitespace-pre-wrap text-sm leading-7">
                          {item.content}
                        </div>
                      </div>
                    ) : (
                      <div className="max-w-[88%] rounded-2xl rounded-bl-md border border-slate-200 bg-white px-5 py-4 text-slate-700 shadow-sm">
                        <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-[#062b5c]">
                          <Scale size={15} className="text-blue-600" />
                          AI Pháp Lý
                        </div>

                        {item.isLoading ? (
                          <div className="flex items-center gap-1.5">
                            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
                            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
                            <span className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
                            <span className="ml-2 text-xs text-slate-400">
                              Đang tra cứu và xử lý...
                            </span>
                          </div>
                        ) : (
                          <div className="whitespace-pre-wrap text-sm leading-7">
                            {item.content}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                <div ref={chatEndRef} />
              </div>
            )}
          </div>

          {/* QUICK QUESTIONS */}
          {history.length > 0 && (
            <div className="border-t border-slate-100 bg-white px-4 py-3">
              <div className="mx-auto flex max-w-3xl flex-wrap gap-2">
                {quickQuestions.map((item, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => handleQuickQuestion(item)}
                    className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs text-slate-600 transition hover:border-blue-200 hover:bg-blue-50 hover:text-blue-700"
                  >
                    {item}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* INPUT */}
          <div className="border-t border-slate-200 bg-white p-4 md:p-5">
            <div className="mx-auto flex max-w-3xl items-end gap-3 rounded-2xl border border-slate-200 bg-slate-50 p-2 shadow-inner focus-within:border-blue-300 focus-within:ring-2 focus-within:ring-blue-100">
              <textarea
                ref={inputRef}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={1}
                placeholder="Nhập câu hỏi pháp lý..."
                className="max-h-32 min-h-[44px] flex-1 resize-none bg-transparent px-3 py-2.5 text-sm outline-none placeholder:text-slate-400"
              />

              <button
                type="button"
                onClick={handleAskAI}
                disabled={loading || !question.trim()}
                className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#062b5c] text-white shadow-md transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40"
                title="Gửi câu hỏi"
              >
                <Send size={18} />
              </button>
            </div>

            <div className="mx-auto mt-2 max-w-3xl text-center text-[11px] text-slate-400">
              Enter để gửi • Shift + Enter để xuống dòng
            </div>
          </div>
        </section>

        {/* FEATURES */}
        <div className="mx-auto mt-8 grid max-w-4xl gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm">
            <Search className="mb-3 text-blue-600" size={21} />
            <h3 className="font-semibold text-[#062b5c]">
              Local RAG
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Ưu tiên truy xuất dữ liệu pháp lý nội bộ từ Qdrant.
            </p>
          </div>

          <div className="rounded-2xl border border-indigo-100 bg-white p-5 shadow-sm">
            <Sparkles className="mb-3 text-indigo-600" size={21} />
            <h3 className="font-semibold text-[#062b5c]">
              Qwen2.5-7B + LoRA
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Mô hình chuyên biệt xử lý và diễn giải câu hỏi pháp lý.
            </p>
          </div>

          <div className="rounded-2xl border border-emerald-100 bg-white p-5 shadow-sm">
            <ShieldCheck className="mb-3 text-emerald-600" size={21} />
            <h3 className="font-semibold text-[#062b5c]">
              MCP External
            </h3>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Có thể tra cứu Cổng Dịch vụ công khi Local RAG không đủ dữ liệu.
            </p>
          </div>
        </div>
      </main>

      {/* FOOTER */}
      <footer className="mt-10 border-t border-blue-900/20 bg-[#061f42] text-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-5 py-6 text-sm text-blue-100 md:flex-row md:items-center md:justify-between">
          <div>© 2026 AI Pháp Lý — DAI-Legal-Model</div>
          <div>Hệ thống hỗ trợ tra cứu và giải thích thông tin pháp luật</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
