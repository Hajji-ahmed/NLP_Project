# 🚀 Déploiement de LLM avec Qwen2.5-0.5B, FastAPI et Gradio

Projet complet de déploiement d'un modèle de langage (LLM) open-source avec API et interface web utilisant le modèle **Qwen2.5-0.5B-Instruct** d'Alibaba Cloud.

## 📁 Structure du projet

```
NLP_Project/
│── model/            # Modèle Qwen2.5-0.5B-Instruct téléchargé ici
│── api/
│   └── main.py       # API FastAPI
│── web/
│   └── ui.py         # Interface web Gradio
│── logs/
│   └── requests.log  # Logs des requêtes
│── bench/
│   └── load_test.py  # Test de latence / concurrence
│── requirements.txt
│── download_model.py # Script de téléchargement du modèle
└── README.md
```

## 📝 À propos du modèle

**Qwen2.5-0.5B-Instruct** est un modèle de langage compact (500M paramètres) développé par Alibaba Cloud, optimisé pour les tâches d'instruction et de conversation. Ce modèle offre un excellent compromis entre performance et légèreté.

## ✅ Étape 1 — Installation des dépendances

```bash
pip install -r requirements.txt
```

## ✅ Étape 2 — Télécharger le modèle Qwen2.5-0.5B-Instruct

```bash
python download_model.py
```

Cette commande télécharge automatiquement le modèle Qwen2.5-0.5B-Instruct depuis Hugging Face et le sauvegarde dans le dossier `model/`.

## ✅ Étape 3 — Lancer l'API FastAPI

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est maintenant disponible sur `http://localhost:8000`

### Test de l'API

Vous pouvez tester l'endpoint `/generate` avec curl ou un client HTTP :

```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, how are you?", "max_new_tokens": 50}'
```

## ✅ Étape 4 — Lancer l'interface web Gradio

Dans un nouveau terminal :

```bash
python web/ui.py
```

Une page web s'ouvre automatiquement avec une interface simple :
- Zone de texte pour saisir votre prompt
- Le modèle génère une réponse
- Interface type ChatGPT simplifiée

## ✅ Étape 5 — Tester la concurrence et la latence

```bash
python bench/load_test.py
```

Ce script envoie 100 requêtes simultanées et affiche la latence moyenne.

## ✅ Étape 6 — Vérifier les logs

Tous les logs sont enregistrés dans :

```
logs/requests.log
```

Exemple de log :
```
2025-12-06 11:12:30 - INPUT from 127.0.0.1: Bonjour...
2025-12-06 11:12:30 - OUTPUT to 127.0.0.1: latency=0.156s
```

## 🧠 Résultat final

| Partie                        | Statut |
|-------------------------------|--------|
| Charger Qwen2.5-0.5B-Instruct | ✔️     |
| Créer API FastAPI             | ✔️     |
| Endpoint /generate            | ✔️     |
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

## 🎯 Utilisation pour un workshop

Ce projet est prêt pour une démonstration complète de :
1. Chargement d'un modèle Hugging Face
2. Création d'une API REST
3. Interface utilisateur web
4. Tests de performance
5. Monitoring avec logs

Bon workshop ! 🎉
