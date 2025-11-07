# mini_c_compiler.py
import subprocess
import tempfile
import os
import shlex

def mini_c_compiler(source_code):
    """
    Compile and run C source using system gcc.
    Returns a dict: { "compiler_output": str, "program_output": str, "status": "success"|"syntax"|"semantic"|"runtime" }
    """

    # Create temp C file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".c") as tf:
        tf.write(source_code.encode())
        c_path = tf.name

    exe_path = c_path.replace(".c", ".exe") if os.name == "nt" else c_path.replace(".c", "")

    # Compile with warnings enabled (format warnings)
    compile_cmd = ["gcc", "-Wall", "-Wformat", c_path, "-o", exe_path]
    compile_proc = subprocess.run(compile_cmd, capture_output=True, text=True)

    compiler_stderr = compile_proc.stderr.strip()
    compiler_stdout = compile_proc.stdout.strip()

    # If compilation failed (non-zero return code) -> syntax / compile error
    if compile_proc.returncode != 0:
        # Remove temp files
        try:
            os.remove(c_path)
        except:
            pass
        return {
            "compiler_output": compiler_stderr or compiler_stdout or "Compilation failed",
            "program_output": "",
            "status": "syntax"
        }

    # If compiled successfully but gcc emitted warnings, we can classify certain warnings as semantic-like
    # e.g., format warnings: "warning: format '%d' expects a matching..."
    semantic_warning = ""
    if compiler_stderr:
        # look for format-related warnings (simple check)
        lower = compiler_stderr.lower()
        if "format" in lower or "expects" in lower or "warning:" in lower:
            semantic_warning = compiler_stderr

    # Execute the program (catch runtime errors/timeouts)
    try:
        run_proc = subprocess.run([exe_path], capture_output=True, text=True, timeout=5)
        run_stdout = run_proc.stdout.strip()
        run_stderr = run_proc.stderr.strip()

        # runtime non-zero exit code may indicate runtime error
        if run_proc.returncode != 0:
            status = "runtime"
            program_output = (run_stdout + ("\n" + run_stderr if run_stderr else "")).strip()
        else:
            # success but may have semantic warnings
            status = "semantic" if semantic_warning else "success"
            program_output = run_stdout
    except subprocess.TimeoutExpired:
        status = "runtime"
        program_output = "Error: Program timed out."
    except Exception as e:
        status = "runtime"
        program_output = f"Runtime error: {e}"

    # Build user-friendly compiler_output
    if semantic_warning:
        compiler_output = semantic_warning
    else:
        compiler_output = "Compilation successful ✅"

    # Cleanup temp files
    try:
        os.remove(c_path)
    except:
        pass
    try:
        if os.path.exists(exe_path):
            os.remove(exe_path)
    except:
        pass

    return {
        "compiler_output": compiler_output,
        "program_output": program_output,
        "status": status
    }
