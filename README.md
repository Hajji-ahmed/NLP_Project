# 🚀 Déploiement Sécurisé de LLM avec Qwen2.5-0.5B, FastAPI et Gradio

Projet complet de déploiement d'un modèle de langage (LLM) open-source avec une API FastAPI sécurisée et une interface web Gradio. Utilise le modèle **Qwen2.5-0.5B-Instruct** d'Alibaba Cloud avec un système de filtrage de sécurité **Llama-Guard-3-1B**.

## 📁 Structure du projet

```
NLP_Project/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py              # API FastAPI avec authentification
│   │   ├── llm_engine.py         # Moteur LLM (llama-cpp-python)
│   │   └── security.py           # Moteur de sécurité (filtrage + détection)
│   ├── logs/                     # Logs des requêtes API
│   └── models/
│       ├── qwen2.5-0.5b-instruct-q4_k_m.gguf   (À télécharger)
│       └── llama-guard-3-1b-q4_k_m.gguf        (À télécharger)
├── web/
│   ├── __init__.py
│   └── ui.py                     # Interface web Gradio
├── bench/
│   ├── __init__.py
│   └── load_test.py              # Test de performance (latence / concurrence)
├── requirements.txt              # Dépendances Python
└── README.md
```

## 📝 À propos des modèles

- **Qwen2.5-0.5B-Instruct** : Modèle de langage compact (500M paramètres) développé par Alibaba Cloud, optimisé pour les tâches conversationnelles
- **Llama-Guard-3-1B** : Modèle de sécurité pour détecter et filtrer les contenus potentiellement dangereux

## ✅ Étape 1 — Installation des dépendances

```bash
pip install -r requirements.txt
```

## ✅ Étape 2 — Télécharger les modèles manuellement

Les modèles doivent être téléchargés depuis Hugging Face et placés dans le dossier `backend/models/`.

### Télécharger Qwen2.5-0.5B-Instruct
```bash
# Option 1: Avec huggingface_hub
huggingface-cli download Qwen/Qwen2.5-0.5B-Instruct-GGUF qwen2.5-0.5b-instruct-q4_k_m.gguf --local-dir backend/models/
```

Ou visitez manuellement: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF

### Télécharger Llama-Guard-3-1B
```bash
# Option 2: Avec huggingface_hub
huggingface-cli download meta-llama/Llama-Guard-3-1b-GGUF llama-guard-3-1b-q4_k_m.gguf --local-dir backend/models/
```

Ou visitez manuellement: https://huggingface.co/meta-llama/Llama-Guard-3-1b-GGUF

**Vérifiez que les fichiers sont dans `backend/models/` avec les noms exacts :**
```
backend/models/
├── qwen2.5-0.5b-instruct-q4_k_m.gguf
└── llama-guard-3-1b-q4_k_m.gguf
```

## ✅ Étape 3 — Configurer la clé API

Pour lancer l'API, vous devez définir une variable d'environnement `LLM_API_KEY` :

```bash
# Windows (PowerShell)
$env:LLM_API_KEY="votre-clé-secrète"

# Windows (CMD)
set LLM_API_KEY=votre-clé-secrète

# Linux/Mac
export LLM_API_KEY="votre-clé-secrète"
```

## ✅ Étape 4 — Lancer l'API FastAPI

```bash
cd backend
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est maintenant disponible sur `http://localhost:8000`

### Documentation interactive de l'API
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

### Test de l'API

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: votre-clé-secrète" \
  -d '{"text": "Hello, how are you?", "max_new_tokens": 50}'
```

## ✅ Étape 5 — Lancer l'interface web Gradio

Dans un nouveau terminal :

```bash
python web/ui.py
```

Une interface web s'ouvre automatiquement avec :
- Zone de texte pour saisir votre prompt
- Génération de réponses en temps réel
- Interface intuitive type ChatGPT

### Configuration pour accès à distance

Pour accéder à l'API depuis un autre ordinateur, utilisez **Ngrok** :
```bash
ngrok http 8000
```

Mettez à jour l'URL dans `web/ui.py` et `bench/load_test.py` avec l'URL Ngrok généré.

## ✅ Étape 6 — Tester la performance et la concurrence

```bash
cd bench
python load_test.py
```

Ce script envoie 20 requêtes simultanées et affiche :
- Temps de réponse pour chaque requête
- Latence moyenne
- Détection des contenus bloqués

## 🛡️ Système de sécurité en 3 couches

L'API implémente une défense en profondeur :

1. **Couche 1 - Regex** : Filtrage des patterns dangereux courants
2. **Couche 1.5 - DeBERTa** : Détection des injections de prompts
3. **Couche 2 - Llama-Guard** : Classification de sécurité avec le modèle dédié
4. **Couche 3 - XML Escaping** : Neutralisation des caractères spéciaux

## 📊 Logs et monitoring

Tous les logs sont enregistrés dans `backend/logs/requests.log` :

```
2025-12-20 14:32:15 - INPUT from 127.0.0.1: "What is AI?"
2025-12-20 14:32:16 - OUTPUT to 127.0.0.1: latency=1.234s | tokens=45
2025-12-20 14:32:18 - BLOCKED L2: Dangerous content detected
```

## 📦 Dépendances principales

- **FastAPI** : Framework web asynchrone haute performance
- **Uvicorn** : Serveur ASGI
- **llama-cpp-python** : Exécution de modèles GGUF en Python
- **Gradio** : Création d'interfaces web sans code
- **Transformers** : Modèles NLP de Hugging Face
- **Torch** : Framework deep learning
- **python-dotenv** : Gestion des variables d'environnement
- **Pydantic** : Validation de données

## 🧠 Caractéristiques

| Fonctionnalité              | Statut |
|-----------------------------|--------|
| Chargement Qwen2.5-0.5B     | ✔️     |
| Chargement Llama-Guard-3-1B | ✔️     |
| API FastAPI sécurisée       | ✔️     |
| Endpoint `/generate`        | ✔️     |
| Authentification API Key     | ✔️     |
| Filtrage de sécurité        | ✔️     |
| Interface Gradio            | ✔️     |
| Tests de performance        | ✔️     |
| Logs des requêtes           | ✔️     |

## 🔗 Ressources

- [Qwen2.5-0.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)
- [Llama-Guard-3-1B](https://huggingface.co/meta-llama/Llama-Guard-3-1b-GGUF)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gradio Documentation](https://www.gradio.app/)
| Interface web Gradio          | ✔️     |
| Test concurrent & latence     | ✔️     |
| Logging complet               | ✔️     |

## 📊 Caractéristiques du modèle

- **Modèle** : Qwen2.5-0.5B-Instruct
- **Paramètres** : 500M
- **Développeur** : Alibaba Cloud
- **Type** : Modèle instruction-tuned pour la génération de texte et la conversation
- **Avantages** : Compact, rapide, optimisé pour les instructions

## 📝 Notes

- **CPU vs GPU** : Le modèle détecte automatiquement si CUDA est disponible
- **Latence** : Environ 0.1-0.5s par requête selon le matériel
- **Concurrence** : FastAPI gère naturellement les requêtes asynchrones
- **Modèle** : DistilGPT-2 est un modèle léger (82M paramètres) parfait pour un workshop

