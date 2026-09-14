import { useState } from "react";
import {
  Scale,
  MessageCircle,
  FileText,
  BookOpen,
  Menu,
} from "lucide-react";
import { askAI } from "./api";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAskAI = async () => {
    console.log("ĐÃ BẤM HỎI AI");
    console.log("QUESTION:", question);

    if (!question.trim()) {
      setAnswer("Vui lòng nhập câu hỏi.");
      return;
    }

    setLoading(true);
    setAnswer("Đang xử lý...");

    try {
      const result = await askAI(question);

      console.log("AI RESULT:", result);

      setAnswer(result);
    } catch (error) {
      console.error("AI ERROR:", error);
      setAnswer("Lỗi kết nối Core API: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      <div className="bg-[#061B36] text-slate-300 text-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-2">
          <div>Cổng thông tin hỗ trợ pháp lý bằng AI</div>
          <div className="hidden md:block">
            Hỗ trợ trực tuyến • AI Pháp Lý
          </div>
        </div>
      </div>

      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">

          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#062B5C] text-[#F4C430]">
              <Scale size={25} />
            </div>

            <div>
              <div className="text-xl font-bold text-[#062B5C]">
                AI Pháp Lý
              </div>

              <div className="text-xs text-slate-500">
                Hỏi gì - Trả lời đó
              </div>
            </div>
          </div>

          <nav className="hidden items-center gap-8 lg:flex">
            <a href="#home" className="font-medium text-[#062B5C]">
              Trang chủ
            </a>

            <a href="#chat" className="flex items-center gap-2 text-slate-600">
              <MessageCircle size={17} />
              Chat AI
            </a>

            <a href="#procedures" className="flex items-center gap-2 text-slate-600">
              <FileText size={17} />
              Tra cứu thủ tục
            </a>

            <a href="#laws" className="flex items-center gap-2 text-slate-600">
              <BookOpen size={17} />
              Văn bản pháp luật
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <button className="hidden rounded-lg border border-slate-300 px-5 py-2.5 text-sm font-semibold md:block">
              Đăng nhập
            </button>

            <button className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#062B5C] text-white lg:hidden">
              <Menu size={21} />
            </button>
          </div>

        </div>
      </header>

      <main id="home">

        <section className="mx-auto flex min-h-[calc(100vh-112px)] max-w-7xl items-center px-6 py-20">

          <div className="w-full max-w-3xl">

            <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-2 text-sm font-medium text-blue-700">
              <span className="h-2 w-2 rounded-full bg-blue-600"></span>
              Trợ lý pháp lý thông minh
            </div>

            <h1 className="text-5xl font-bold leading-tight tracking-tight text-[#062B5C] md:text-6xl">
              Giải đáp pháp luật
              <br />
              <span className="text-blue-600">
                nhanh chóng bằng AI
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              Đặt câu hỏi về pháp luật, thủ tục hành chính và các quy định
              liên quan. AI Pháp Lý hỗ trợ tìm kiếm và giải thích thông tin
              một cách nhanh chóng, dễ hiểu.
            </p>

            <div
              id="chat"
              className="mt-10 flex max-w-2xl items-center rounded-2xl border border-slate-200 bg-white p-2 shadow-lg"
            >

              <div className="flex flex-1 items-center gap-3 px-4">

                <MessageCircle
                  size={22}
                  className="text-blue-600"
                />

                <input
                  type="text"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleAskAI();
                    }
                  }}
                  placeholder="Bạn muốn hỏi vấn đề pháp lý nào?"
                  className="w-full bg-transparent py-3 text-sm outline-none"
                />

              </div>

              <button
                type="button"
                onClick={handleAskAI}
                className="rounded-xl bg-[#062B5C] px-5 py-3 font-semibold text-white hover:bg-blue-700"
              >
                {loading ? "Đang xử lý..." : "Hỏi AI"}
              </button>

            </div>

            {loading && (
              <div className="mt-5 text-sm text-slate-500">
                AI đang phân tích câu hỏi và tra cứu dữ liệu pháp luật...
              </div>
            )}

            {answer && (
              <div className="mt-8 max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-lg">

                <div className="mb-4 flex items-center gap-2 font-semibold text-[#062B5C]">
                  <MessageCircle size={20} />
                  AI Pháp Lý trả lời
                </div>

                <div className="whitespace-pre-wrap leading-7 text-slate-700">
                  {answer}
                </div>

              </div>
            )}

          </div>

        </section>

      </main>

    </div>
  );
}

export default App;