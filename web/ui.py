import gradio as gr
import requests
import os



API_KEY = "groupe3-secret-key-123"
API_URL = "https://eb0cf532ffbd.ngrok-free.app/generate"

# In web/ui.py on your laptop
def ask_model(text):
    try:
        # This is REQUIRED for Ngrok
        headers = {
            "ngrok-skip-browser-warning": "true",
             "X-API-Key": API_KEY
            }
        
        response = requests.post(API_URL, json={"text": text}, headers=headers)
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"❌ Error {response.status_code}: {response.text}"
            
    except Exception as e:
        return f"❌ Connection Error: {e}"

interface = gr.Interface(
    fn=ask_model,
    inputs="text",
    outputs="text",
    title="Qwen2.5-0.5B",
    description="Écris un texte et le modèle répond."
)

interface.launch()
