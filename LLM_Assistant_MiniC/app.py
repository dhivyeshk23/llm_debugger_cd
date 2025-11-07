from flask import Flask, request, jsonify
from flask_cors import CORS
from llm_assistant_gemini import LLMAssistant
from mini_c_compiler import mini_c_compiler
import serial
import time
import traceback

app = Flask(__name__)
CORS(app)
assistant = LLMAssistant()

# Arduino Connection - Auto-detect port
ARDUINO_CONNECTED = False
arduino = None

def connect_arduino():
    """Try to connect to Arduino on common ports"""
    global arduino, ARDUINO_CONNECTED
    ports = ['/dev/ttyUSB1', '/dev/ttyACM0', 'COM3', 'COM4', 'COM5']
    
    for port in ports:
        try:
            arduino = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)  # Wait for Arduino to initialize
            ARDUINO_CONNECTED = True
            print(f"✅ Arduino Connected on {port}")
            return True
        except Exception:
            continue
    
    print("⚠️ Arduino Not Connected - Running in simulation mode")
    return False

connect_arduino()

def send_signal(code: str):
    """Send signal to Arduino to control LEDs"""
    if ARDUINO_CONNECTED and arduino:
        try:
            arduino.write(code.encode())
            arduino.flush()
            print(f"📡 Sent signal: {code}")
        except Exception as e:
            print(f"⚠️ Arduino write error: {e}")
    else:
        print(f"[SIMULATION] LED Signal → {code}")

@app.route("/")
def home():
    status = "Connected" if ARDUINO_CONNECTED else "Simulation Mode"
    return f"Mini C Compiler Backend Running ✅ | Arduino: {status}"

@app.route("/compile", methods=["POST"])
def compile_code():
    try:
        source_code = request.json.get("source_code", "").strip()
        
        if not source_code:
            return jsonify({
                "compiler_output": "Error: Empty source code",
                "program_output": "",
                "status": "error",
                "llm_feedback": "Please provide valid C code to compile.",
                "corrected_code": ""
            })
        
        # Compile the code
        result = mini_c_compiler(source_code)
        
        compiler_output = result.get("compiler_output", "")
        program_output = result.get("program_output", "")
        status = result.get("status", "unknown")
        
        llm_feedback = ""
        corrected_code = ""
        
        # Only get LLM feedback and corrections if there's an error
        if status != "success":
            try:
                # Get LLM feedback for errors
                llm_feedback = assistant.analyze_error(compiler_output, source_code)
                if not llm_feedback:
                    llm_feedback = "Error detected but no specific feedback available."
            except Exception as e:
                llm_feedback = f"LLM analysis unavailable: {str(e)}"
                print(f"LLM Feedback Error: {traceback.format_exc()}")
            
            try:
                # Get corrected code only on errors
                corrected = assistant.fix_code(source_code)
                if corrected and corrected.strip() and corrected.strip() != source_code.strip():
                    corrected_code = corrected
                else:
                    corrected_code = ""
            except Exception as e:
                corrected_code = ""
                print(f"Code Fix Error: {traceback.format_exc()}")
        else:
            # Success case
            llm_feedback = "✅ Code compiled and executed successfully!"
            corrected_code = ""  # No correction needed
        
        # Send LED signals based on error type
        if status == "success":
            send_signal('S')  # Green LED
        elif status == "syntax":
            send_signal('X')  # Red LED
        elif status == "semantic":
            send_signal('M')  # Yellow LED
        elif status == "runtime":
            send_signal('R')  # Blue LED
        else:
            send_signal('O')  # Turn off all LEDs
        
        return jsonify({
            "compiler_output": compiler_output,
            "program_output": program_output,
            "status": status,
            "llm_feedback": llm_feedback,
            "corrected_code": corrected_code
        })
        
    except Exception as e:
        traceback.print_exc()
        send_signal('O')  # Turn off LEDs on server error
        return jsonify({
            "compiler_output": f"Server error: {str(e)}",
            "program_output": "",
            "status": "error",
            "llm_feedback": "An unexpected server error occurred. Please try again.",
            "corrected_code": ""
        }), 500

@app.route("/fix", methods=["POST"])
def fix_code():
    """Standalone endpoint to fix code (optional, not used in main flow)"""
    try:
        source_code = request.json.get("source_code", "").strip()
        
        if not source_code:
            return jsonify({
                "corrected_code": "",
                "explanation": "No source code provided"
            })
        
        corrected = assistant.fix_code(source_code)
        explanation = assistant.analyze_error("", source_code)
        
        return jsonify({
            "corrected_code": corrected if corrected else "",
            "explanation": explanation if explanation else "No issues detected"
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "corrected_code": "",
            "explanation": f"Error: {str(e)}"
        }), 500

@app.route("/arduino/status", methods=["GET"])
def arduino_status():
    """Check Arduino connection status"""
    return jsonify({
        "connected": ARDUINO_CONNECTED,
        "port": arduino.port if arduino else None
    })

if __name__ == "__main__":
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    finally:
        if arduino:
            arduino.close()
            print("Arduino connection closed")