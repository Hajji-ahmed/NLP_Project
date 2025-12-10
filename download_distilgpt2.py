"""
Script pour télécharger DistilGPT-2 (modèle léger et rapide)
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import os

print("📥 Téléchargement de DistilGPT-2...", flush=True)

tokenizer = AutoTokenizer.from_pretrained("distilgpt2")
print("✓ Tokenizer téléchargé", flush=True)

model = AutoModelForCausalLM.from_pretrained("distilgpt2")
print("✓ Modèle téléchargé", flush=True)

if not os.path.exists("model"):
    os.makedirs("model")

tokenizer.save_pretrained("model/")
model.save_pretrained("model/")

print("✅ DistilGPT-2 sauvegardé dans model/", flush=True)
