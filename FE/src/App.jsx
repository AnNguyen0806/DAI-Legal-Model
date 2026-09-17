import { useState } from "react";
import {
  Scale,
  MessageCircle,
  FileText,
  BookOpen,
  Send,
  Sparkles,
  ShieldCheck,
  Search,
  ArrowRight,
} from "lucide-react";
import { askAI } from "./api";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAskAI = async () => {
    if (!question.trim()) {
      setAnswer("Vui lòng nhập câu hỏi.");
      return;
    }

    setLoading(true);
    setAnswer("");

    try {
      const result = await askAI(question);
      setAnswer(result);
    } catch (error) {
      console.error("AI ERROR:", error);
      setAnswer("Lỗi kết nối Core API: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const quickQuestions = [
    "Thủ tục đăng ký tạm trú cần những giấy tờ gì?",
    "Đăng ký tạm trú có mất phí không?",
    "Đăng ký kết hôn cần những giấy tờ gì?",
  ];

  return (
    <div className="min-h-screen overflow-hidden bg-gradient-to-br from-slate-50 via-white to-blue-50 text-slate-900">

      {/* TOP BAR */}
      <div className="bg-[#061f42] text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-2 text-xs md:text-sm">
          <div className="flex items-center gap-2">
            <ShieldCheck size={15} />
            Cổng thông tin hỗ trợ pháp lý bằng AI
          </div>

          <div className="hidden md:block text-slate-300">
            Hỗ trợ trực tuyến • AI Pháp Lý
          </div>
        </div>
      </div>

      {/* HEADER */}
      <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-[76px] max-w-7xl items-center justify-between px-6">

          {/* LOGO */}
          <a href="#home" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#062b5c] shadow-sm">
              <Scale size={25} className="text-[#f4c430]" />
            </div>

            <div>
              <div className="text-xl font-bold tracking-tight text-[#062b5c]">
                AI Pháp Lý
              </div>

              <div className="text-xs text-slate-500">
                Hỏi gì · Trả lời đó
              </div>
            </div>
          </a>

          {/* NAVIGATION */}
          <nav className="hidden items-center gap-8 lg:flex">

            <a
              href="#home"
              className="font-semibold text-[#062b5c] transition hover:text-blue-600"
            >
              Trang chủ
            </a>

            <a
              href="#chat"
              className="flex items-center gap-2 text-slate-600 transition hover:text-blue-600"
            >
              <MessageCircle size={17} />
              Chat AI
            </a>

            <a
              href="#procedures"
              className="flex items-center gap-2 text-slate-600 transition hover:text-blue-600"
            >
              <FileText size={17} />
              Tra cứu thủ tục
            </a>

            <a
              href="#laws"
              className="flex items-center gap-2 text-slate-600 transition hover:text-blue-600"
            >
              <BookOpen size={17} />
              Văn bản pháp luật
            </a>

          </nav>

          {/* STATUS */}
          <div className="hidden items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-medium text-emerald-700 md:flex">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            AI đang hoạt động
          </div>

        </div>
      </header>

      {/* HERO */}
      <main id="home">

        <section className="relative overflow-hidden bg-gradient-to-b from-white via-blue-50/40 to-indigo-50/30">

          {/* background decoration */}
          <div className="absolute -left-32 top-20 h-72 w-72 rounded-full bg-blue-100/50 blur-3xl" />
          <div className="absolute -right-32 top-10 h-80 w-80 rounded-full bg-indigo-100/50 blur-3xl" />

          <div className="absolute left-1/2 top-24 h-64 w-64 -translate-x-1/2 rounded-full bg-cyan-200/20 blur-3xl" />
          <div className="relative mx-auto max-w-7xl px-6 pb-20 pt-20 md:pb-28 md:pt-24">

            <div className="mx-auto max-w-4xl text-center">

              {/* BADGE */}
              <div className="mb-7 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50/90 px-4 py-2 text-sm font-semibold text-blue-700 shadow-sm shadow-blue-100">
                <Sparkles size={16} />
                Trợ lý pháp lý thông minh
              </div>

              {/* TITLE */}
              <h1 className="text-4xl font-extrabold leading-tight tracking-tight text-[#062b5c] sm:text-5xl md:text-6xl">

                Giải đáp pháp luật

                <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  nhanh chóng bằng AI
                </span>

              </h1>

              {/* DESCRIPTION */}
              <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-600 md:text-lg">
                Đặt câu hỏi về pháp luật, thủ tục hành chính và các quy định
                liên quan. AI Pháp Lý hỗ trợ tìm kiếm và giải thích thông tin
                một cách nhanh chóng, dễ hiểu.
              </p>

              {/* CHAT BOX */}
              <div
                id="chat"
                className="mx-auto mt-10 max-w-3xl rounded-3xl border border-blue-200/70 bg-white/95 p-2 shadow-2xl shadow-blue-200/40 ring-1 ring-blue-100/60"
              >

                <div className="flex items-center gap-3">

                  <div className="hidden h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-50 to-indigo-100 text-blue-600 sm:flex">
                    <Search size={21} />
                  </div>

                  <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !loading) {
                        handleAskAI();
                      }
                    }}
                    placeholder="Bạn muốn hỏi vấn đề pháp lý nào?"
                    className="min-w-0 flex-1 bg-transparent px-3 py-4 text-sm outline-none placeholder:text-slate-400 md:text-base"
                  />

                  <button
                    type="button"
                    onClick={handleAskAI}
                    disabled={loading}
                    className="flex items-center gap-2 rounded-2xl bg-gradient-to-r from-[#062b5c] via-blue-700 to-indigo-700 px-5 py-3.5 font-semibold text-white shadow-lg shadow-blue-200 transition hover:-translate-y-0.5 hover:from-blue-700 hover:to-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    <span className="hidden sm:inline">
                      {loading ? "Đang xử lý..." : "Hỏi AI"}
                    </span>

                    <Send size={18} />
                  </button>

                </div>

              </div>

              {/* LOADING */}
              {loading && (
                <div className="mx-auto mt-5 flex max-w-3xl items-center justify-center gap-2 text-sm text-slate-500">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-blue-600" />
                  AI đang phân tích câu hỏi và tra cứu dữ liệu pháp luật...
                </div>
              )}

            </div>

            {/* QUICK QUESTIONS */}
            <div className="mx-auto mt-8 max-w-3xl">

              <div className="mb-3 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">
                Câu hỏi phổ biến
              </div>

              <div className="flex flex-wrap justify-center gap-2">

                {quickQuestions.map((item, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setQuestion(item);
                      setAnswer("");
                    }}
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

            {/* ANSWER */}
            {answer && (
              <div className="mx-auto mt-10 max-w-3xl">

                <div className="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-xl shadow-slate-200/50">

                  {/* ANSWER HEADER */}
                  <div className="flex items-center gap-3 border-b border-slate-100 bg-gradient-to-r from-[#062b5c] to-[#0b4389] px-6 py-4 text-white">

                    <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-white/15">
                      <Scale size={19} className="text-[#f4c430]" />
                    </div>

                    <div>
                      <div className="font-semibold">
                        AI Pháp Lý
                      </div>

                      <div className="text-xs text-blue-100">
                        Kết quả tư vấn từ hệ thống RAG
                      </div>
                    </div>

                  </div>

                  {/* ANSWER CONTENT */}
                  <div className="p-6 md:p-8">

                    <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-[#062b5c]">
                      <MessageCircle size={18} />
                      Nội dung trả lời
                    </div>

                    <div className="whitespace-pre-wrap text-[15px] leading-8 text-slate-700">
                      {answer}
                    </div>

                  </div>

                </div>

              </div>
            )}

            {/* FEATURES */}
            <div className="mx-auto mt-16 grid max-w-4xl gap-4 md:grid-cols-3">

              <div className="rounded-2xl border border-blue-100 bg-white/90 p-5 shadow-lg shadow-blue-100/50 transition hover:-translate-y-1 hover:shadow-xl hover:shadow-blue-100/70">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <Search size={20} />
                </div>

                <h3 className="font-semibold text-[#062b5c]">
                  Tra cứu thông minh
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Tìm kiếm thông tin pháp luật từ cơ sở dữ liệu được tích hợp.
                </p>
              </div>

              <div className="rounded-2xl border border-indigo-100 bg-white/90 p-5 shadow-lg shadow-indigo-100/50 transition hover:-translate-y-1 hover:shadow-xl hover:shadow-indigo-100/70">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                  <Sparkles size={20} />
                </div>

                <h3 className="font-semibold text-[#062b5c]">
                  AI chuyên biệt
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Qwen2.5-7B kết hợp LoRA để hỗ trợ xử lý câu hỏi pháp lý.
                </p>
              </div>

              <div className="rounded-2xl border border-emerald-100 bg-white/90 p-5 shadow-lg shadow-emerald-100/50 transition hover:-translate-y-1 hover:shadow-xl hover:shadow-emerald-100/70">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                  <ShieldCheck size={20} />
                </div>

                <h3 className="font-semibold text-[#062b5c]">
                  Có dữ liệu đối chiếu
                </h3>

                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Hệ thống sử dụng RAG để truy xuất thông tin trước khi trả lời.
                </p>
              </div>

            </div>

          </div>

        </section>

      </main>

      {/* FOOTER */}
      <footer className="border-t border-blue-900/20 bg-gradient-to-r from-[#061f42] via-[#062b5c] to-[#102a72] text-white">

        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-6 py-8 text-sm text-blue-100 md:flex-row md:items-center md:justify-between">

          <div>
            © 2026 AI Pháp Lý — DAI-Legal-Model
          </div>

          <div>
            Hệ thống hỗ trợ tra cứu và giải thích thông tin pháp luật
          </div>

        </div>

      </footer>

    </div>
  );
}

export default App;