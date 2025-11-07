import google.generativeai as genai

genai.configure(api_key="AIzaSyA4l2yuTldjxRjcjVIOpIitsXwVs-4Vmrc")

print("🔍 Available Gemini Models:\n")
for model in genai.list_models():
    print(model.name)
