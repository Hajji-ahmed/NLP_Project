"""
Script pour télécharger le modèle Qwen2.5-0.5B-Instruct
Exécuter ce script une seule fois pour télécharger le modèle
"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import os
import sys

print("📥 Téléchargement de Qwen2.5-0.5B-Instruct...", flush=True)

try:
    # Télécharger seulement le tokenizer et les configs
    print("Téléchargement du tokenizer...", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(
        "Qwen/Qwen2.5-0.5B-Instruct",
        trust_remote_code=True
    )
    print("✓ Tokenizer téléchargé", flush=True)
    
    print("Téléchargement des fichiers de configuration...", flush=True)
    # On ne charge pas le modèle en mémoire, juste téléchargement
    from huggingface_hub import snapshot_download
    snapshot_download(
        "Qwen/Qwen2.5-0.5B-Instruct",
        local_dir="model/",
        local_dir_use_symlinks=False
    )
    print("✓ Modèle téléchargé", flush=True)
    
    print("✅ Modèle téléchargé et sauvegardé avec succès!", flush=True)
    
except KeyboardInterrupt:
    print("\n⚠️ Téléchargement interrompu par l'utilisateur", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur : {e}", flush=True)
    import traceback
    traceback.print_exc()
