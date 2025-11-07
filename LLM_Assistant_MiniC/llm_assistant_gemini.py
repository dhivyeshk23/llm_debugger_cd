import google.generativeai as genai

class LLMAssistant:
    def __init__(self):
        # Initialize Gemini client with your actual API key
        genai.configure(api_key="AIzaSyA4l2yuTldjxRjcjVIOpIitsXwVs-4Vmrc")
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")  # or "gemini-1.5-flash"
    
    def analyze_error(self, compiler_output, source_code=""):
        prompt = f"""
        You are an intelligent debugging assistant for a Mini C Compiler.
        The compiler produced this output:
        
        --- Compiler Output ---
        {compiler_output}
        
        --- Source Code ---
        {source_code}
        
        Please:
        1️⃣ Identify the error type (Syntax, Semantic, Runtime, or Success)
        2️⃣ Give a clear explanation for a beginner in compiler design.
        3️⃣ Suggest how to fix the issue.
        
        Format the output exactly as:
        🧩 Error Type: <type>
        📘 Explanation: <explanation>
        🛠️ Fix Suggestion: <suggestion>
        """
        
        # Generate AI response using the correct API
        response = self.model.generate_content(prompt)
        return response.text
    
    def fix_code(self, source_code):
        prompt = f"Fix this C code, keep logic same. Return ONLY corrected code:\n\n{source_code}"
        response = self.client.models.generate_content(model=self.model, contents=prompt)
        return response.text.strip()