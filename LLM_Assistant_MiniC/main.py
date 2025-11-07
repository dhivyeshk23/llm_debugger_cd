from llm_assistant_gemini import LLMAssistant
from mini_c_compiler import mini_c_compiler
# from arduino_led import indicate_error   # Uncomment if you want LED integration

def run_llm_assistant(source_code):
    print("🔧 Mini C Compiler + Gemini LLM Assistant\n")

    compiler_output = mini_c_compiler(source_code)

    assistant = LLMAssistant()
    feedback = assistant.analyze_error(compiler_output, source_code)

    print(f"Compiler Output:\n{compiler_output}\n")
    print(feedback)

    # Optional: LED integration
    # if "successful" in compiler_output.lower():
    #     indicate_error("success")
    # else:
    #     indicate_error("error")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    # Example code — you can replace this or add multiple tests
    source_code = """
    int main(){
        
        printf("HI DHARSHANA");
        
        return 0;
    }
    """
    run_llm_assistant(source_code)
