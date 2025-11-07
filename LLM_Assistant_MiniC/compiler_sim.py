def compile_code(source):
    lines = [line.strip() for line in source.splitlines() if line.strip()]

    for line in lines:
        # Skip lines that don't need semicolons
        if line.startswith("int main") or line.startswith("{") or line.startswith("}") or line.startswith("//"):
            continue

        # Check for missing semicolon at the end of executable lines
        if not line.endswith(";") and not line.endswith("{") and not line.endswith("}"):
            return "Missing semicolon"

    # Other simulated checks
    if "int" in source and "float" in source:
        return "Type mismatch"
    elif "/ 0" in source:
        return "Division by zero"

    return "Compilation successful"
