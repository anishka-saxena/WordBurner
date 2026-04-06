# WordBurner 🔥
### *Vocabulary learning with zero mercy* 😂

> An AI-powered vocabulary app that teaches English words through sarcastic roast-style explanations — built with microservices and deployed on Kubernetes.

---

## What It Does

Type any word and WordBurner will:

- 🔥 **Roast you** for not knowing it
- 📖 Teach you the **meaning, synonyms, antonyms**
- 🔊 Show **phonetic pronunciation** with audio
- 🧠 Give **memory tricks** and word origin
- 🃏 Navigate through **flashcards** (no endless scrolling)
- 🎲 **Surprise you** with a new word by difficulty level — no repeats, ever

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Streamlit (Python) |
| Backend | FastAPI (Python) |
| AI | Groq API — `llama-3.3-70b-versatile` |
| Pronunciation | gTTS + dictionaryapi.dev |
| Word History | Redis 7 (Alpine) |
| Containerization | Docker (multi-stage builds) |
| Orchestration | Kubernetes (k3s homelab) |
| Ingress | Traefik |
| Registry | DockerHub |

---

## Architecture

```
User (browser)
      │ HTTP
      ▼
Traefik Ingress (k3s)
      │
      ▼
Streamlit Pod (port 8501)
      │ HTTP /roast/{word}
      │ HTTP /surprise/{level}
      ▼
FastAPI Pod (port 8000)
      │                  │
      │ Groq SDK         │ Redis client
      ▼                  ▼
Groq API (external)   Redis Pod (port 6379)
                      used_words:beginner
                      used_words:intermediate
                      used_words:advanced
```

```mermaid
flowchart TD
    A[👤 User browser] -->|HTTP request| B[Traefik Ingress]

    subgraph K8s Cluster — k3s homelab
        B --> C[🖥️ Streamlit Pod\nport 8501]
        C -->|HTTP /roast/word| D[⚡ FastAPI Pod\nport 8000]
        C -->|HTTP /surprise/level| D
        D <-->|used_words:level| R[🗄️ Redis Pod\nport 6379]
        E[🔑 K8s Secret\nGROQ_API_KEY] -.->|env var| D
        G[🐳 DockerHub\nImage registry] -.->|pulls image| D
    end

    D -->|Groq SDK| H[🤖 Groq API\nllama-3.3-70b]
```

---

## Project Structure

```
WordBurner/
├── main.py                     # FastAPI backend + Redis logic
├── roast.py                    # Groq AI prompts & functions
├── streamlit_app.py            # Streamlit frontend
├── requirements.txt            # Python dependencies
├── Dockerfile.fastapi          # Multi-stage Docker build
├── Dockerfile.streamlit        # Multi-stage Docker build
├── .dockerignore               # Excludes venv, secrets
├── .gitignore                  # Excludes .env, venv, secret.yaml
└── k8s/
    ├── secret.yaml             # K8s secret (git-ignored)
    ├── fastapi-deployment.yaml
    ├── fastapi-svc.yaml
    ├── streamlit-deployment.yaml
    ├── streamlit-svc.yaml
    ├── redis-deployment.yaml
    ├── redis-service.yaml
    └── ingress.yaml
```

---

## Local Setup

```bash
# Clone repo
git clone https://github.com/anishka-saxena/WordBurner.git
cd WordBurner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Terminal 1 — Start Redis
docker run -d -p 6379:6379 redis:7-alpine

# Terminal 2 — Start FastAPI
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 3 — Start Streamlit
streamlit run streamlit_app.py
```

Open [http://localhost:8501](http://localhost:8501) 🔥

---

## Docker Setup

```bash
# Build images
docker build -f Dockerfile.fastapi -t wordburner-fastapi:v3 .
docker build -f Dockerfile.streamlit -t wordburner-streamlit:v1 .

# Run Redis
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run FastAPI
docker run -p 8000:8000 \
  -e GROQ_API_KEY=your_key \
  -e REDIS_HOST=host.docker.internal \
  wordburner-fastapi:v3

# Run Streamlit
docker run -p 8501:8501 \
  -e FASTAPI_URL=http://host.docker.internal:8000 \
  wordburner-streamlit:v1
```

---

## Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace wordburner

# Create secret (encode key first)
echo -n "your_groq_key" | base64
# paste output into k8s/secret.yaml

# Deploy everything
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/fastapi-deployment.yaml
kubectl apply -f k8s/fastapi-svc.yaml
kubectl apply -f k8s/streamlit-deployment.yaml
kubectl apply -f k8s/streamlit-svc.yaml
kubectl apply -f k8s/ingress.yaml

# Verify
kubectl get all -n wordburner
```

---

## Key Learnings

- Microservices separation — FastAPI + Streamlit as distinct services
- Redis as persistent shared state across pod restarts and sessions
- Multi-stage Docker builds for lean production images
- K8s secrets management — never commit keys to Git
- Traefik ingress controller setup on k3s
- LLM prompt engineering for consistent structured output
- Temperature tuning for randomness in AI word selection
- Cloudflare Quick Tunnels for homelab public access

---

## Roadmap

- [x] Redis for persistent word history (no repeated surprise words)
- [x] Cloudflare tunnel for public access
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Oracle Cloud free tier deployment
- [ ] Word history and favourites feature

---

## Author

**Anishka Saxena** — CKA Certified DevOps Engineer learning AI Development
