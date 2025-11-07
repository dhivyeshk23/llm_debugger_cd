// src/pages/Index.tsx
import { useState } from "react";
import Editor from "@monaco-editor/react";
import { useTheme } from "@/contexts/ThemeContext";
import { ThemeToggle } from "@/components/ThemeToggle";

type CompilationStatus = "success" | "syntax" | "semantic" | "runtime" | "error" | "unknown";

export default function Index() {
  const { theme } = useTheme();

  const [code, setCode] = useState(`#include <stdio.h>
int main() {
  printf("Hello, World!\\n");
  return 0;
}`);

  const [compilerOutput, setCompilerOutput] = useState("");
  const [programOutput, setProgramOutput] = useState("");
  const [llmFeedback, setLLMFeedback] = useState("");
  const [correctedCode, setCorrectedCode] = useState("");
  const [status, setStatus] = useState<CompilationStatus>("unknown");
  const [showReplace, setShowReplace] = useState(false);
  const [loading, setLoading] = useState(false);

  const getStatusBadge = () => {
    const badges = {
      success: { text: "✅ Success", color: "bg-green-600" },
      syntax: { text: "❌ Syntax Error", color: "bg-red-600" },
      semantic: { text: "⚠️ Semantic Error", color: "bg-yellow-600" },
      runtime: { text: "💥 Runtime Error", color: "bg-blue-600" },
      error: { text: "🔥 Error", color: "bg-red-700" },
      unknown: { text: "⚪ Ready", color: "bg-gray-600" }
    };

    const badge = badges[status] || badges.unknown;
    return (
      <span className={`px-3 py-1 rounded-full text-white text-sm font-semibold ${badge.color}`}>
        {badge.text}
      </span>
    );
  };

  const runCode = async () => {
    setLoading(true);
    setShowReplace(false);
    setStatus("unknown");

    setCompilerOutput("⏳ Compiling...");
    setProgramOutput("⏳ Waiting for compilation...");
    setLLMFeedback("⏳ Analyzing code...");
    setCorrectedCode("");

    try {
      const res = await fetch("http://127.0.0.1:5000/compile", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_code: code }),
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }

      const data = await res.json();

      setCompilerOutput(data.compiler_output || "// No compiler output");
      setProgramOutput(data.program_output || "// No program output");
      setLLMFeedback(data.llm_feedback || "// No feedback available");
      setStatus(data.status || "unknown");

      // Handle corrected code
      const corrected = data.corrected_code?.trim() || "";
      
      if (corrected && corrected !== code.trim()) {
        setCorrectedCode(corrected);
        setShowReplace(true);
      } else if (data.status === "success") {
        setCorrectedCode("✅ No corrections needed - code is perfect!");
      } else {
        setCorrectedCode("// No corrected code available");
      }

    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      setCompilerOutput(`❌ Connection Error: ${errorMsg}\n\nMake sure the Flask backend is running on http://127.0.0.1:5000`);
      setProgramOutput("");
      setLLMFeedback("Unable to connect to backend server");
      setStatus("error");
    }

    setLoading(false);
  };

  const useCorrected = () => {
    if (!correctedCode || 
        correctedCode.startsWith("//") || 
        correctedCode.startsWith("✅")) {
      return;
    }
    setCode(correctedCode);
    setShowReplace(false);
    setCompilerOutput("");
    setProgramOutput("");
    setLLMFeedback("Code replaced! Click 'Run Code' to test the corrected version.");
    setCorrectedCode("");
    setStatus("unknown");
  };

  return (
    <div className="min-h-screen p-6 space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Mini C Compiler + LLM Debugger</h1>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            AI-powered error detection and code correction
          </p>
        </div>
        <div className="flex items-center gap-4">
          {getStatusBadge()}
          <ThemeToggle />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT SIDE */}
        <div className="space-y-4">
          <div className="panel">
            <h2 className="font-semibold mb-2 flex items-center justify-between">
              <span>📝 Source Code</span>
              <span className="text-xs text-gray-500">C Programming</span>
            </h2>
            <Editor
              height="320px"
              theme={theme === "dark" ? "vs-dark" : "light"}
              language="c"
              value={code}
              onChange={(v) => setCode(v ?? "")}
              options={{ 
                automaticLayout: true, 
                minimap: { enabled: false },
                fontSize: 14,
                lineNumbers: "on",
                scrollBeyondLastLine: false
              }}
            />

            <button 
              onClick={runCode} 
              className="button mt-3 w-full" 
              disabled={loading}
            >
              {loading ? "⏳ Running..." : "▶️ Run Code"}
            </button>
          </div>

          <div className="panel">
            <h2 className="font-semibold mb-2">🔧 Compiler Output</h2>
            <pre className="terminal max-h-48 overflow-y-auto">{compilerOutput}</pre>
          </div>
        </div>

        {/* RIGHT SIDE */}
        <div className="space-y-4">
          <div className="panel">
            <h2 className="font-semibold mb-2">📤 Program Output</h2>
            <pre className="terminal max-h-48 overflow-y-auto">{programOutput}</pre>
          </div>

          <div className="panel">
            <h2 className="font-semibold mb-2">🤖 LLM Feedback</h2>
            <pre className="terminal max-h-32 overflow-y-auto whitespace-pre-wrap">
              {llmFeedback}
            </pre>

            <h3 className="font-semibold mt-4 mb-2">✨ Corrected Code</h3>
            <pre className="terminal max-h-48 overflow-y-auto">
              {correctedCode || "// Run your code to get corrections"}
            </pre>

            {showReplace && (
              <button 
                onClick={useCorrected} 
                className="button mt-3 w-full bg-green-600 hover:bg-green-700"
              >
                ✅ Replace with Corrected Code
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}