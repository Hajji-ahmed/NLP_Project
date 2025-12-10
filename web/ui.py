import gradio as gr
import requests

API_URL = "http://localhost:8000/generate"

def ask_model(text):
    response = requests.post(API_URL, json={"text": text})
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Erreur API"

interface = gr.Interface(
    fn=ask_model,
    inputs="text",
    outputs="text",
    title="Qwen2.5-0.5B",
    description="Écris un texte et le modèle répond."
)

interface.launch()
