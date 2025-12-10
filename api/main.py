from fastapi import FastAPI, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import time, logging, os

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------
logging.basicConfig(
    filename="logs/requests.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# ------------------------------------------------------------
# Charger le modèle UNE SEULE FOIS (en RAM)
# ------------------------------------------------------------
MODEL_DIR = "model/"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)

# Chargement normal du modèle
model = AutoModelForCausalLM.from_pretrained(
    MODEL_DIR,
    trust_remote_code=True
).to(device)
model.eval()

# ------------------------------------------------------------
# App FastAPI
# ------------------------------------------------------------
app = FastAPI()

class Prompt(BaseModel):
    text: str
    max_new_tokens: int = 50

@app.post("/generate")
async def generate(data: Prompt, request: Request):
    start = time.time()

    # Logging input
    logging.info(f"INPUT from {request.client.host}: {data.text[:50]}...")

    inputs = tokenizer(data.text, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_new_tokens=data.max_new_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,              # Nucleus sampling
            repetition_penalty=1.1  # Évite les répétitions
        )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    latency = time.time() - start

    # Logging output + latency
    logging.info(f"OUTPUT to {request.client.host}: latency={latency:.3f}s")

    return {
        "response": result,
        "latency": latency
    }
