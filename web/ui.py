import gradio as gr
import requests

API_KEY = "groupe3-secret-key-123"
API_URL = "https://8b95035ff852.ngrok-free.app/generate"

def ask_model(message, history):
    try:
        headers = {
            "ngrok-skip-browser-warning": "true",
            "X-API-Key": API_KEY
        }
        
        # Send request to your API
        response = requests.post(API_URL, json={"text": message}, headers=headers)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"❌ Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ Connection Error: {e}"

# Minimal ChatInterface configuration
interface = gr.ChatInterface(
    fn=ask_model,
    title="🤖 Qwen2.5 Chatbot",
    description="Ask me anything...",
    examples=["Hello!", "Explain quantum physics", "Write a Python script"]
    # We removed 'retry_btn', 'undo_btn', 'type', and 'theme' from here
)

if __name__ == "__main__":
    # Theme is applied here in Gradio 6.0
    interface.launch(theme="soft")