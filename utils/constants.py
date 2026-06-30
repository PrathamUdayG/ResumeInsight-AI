"""
constants.py - Centralized configuration and constant values.

All magic numbers, default settings, and configuration values are defined here
to keep the codebase maintainable and easily adjustable.
"""

# ─────────────────────────── Model Configuration ───────────────────────────

GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384  # Dimension of all-MiniLM-L6-v2 embeddings

# ─────────────────────────── Chunking Settings ─────────────────────────────

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# ─────────────────────────── Retrieval Settings ────────────────────────────

TOP_K = 5
SIMILARITY_THRESHOLD = 0.3  # Minimum cosine similarity for relevant results

# ─────────────────────────── ATS Score Weights ─────────────────────────────
# Weights must sum to 1.0 (100%)

ATS_WEIGHTS = {
    "keyword_match": 0.30,
    "skill_match": 0.20,
    "experience_match": 0.15,
    "education_match": 0.10,
    "formatting": 0.05,
    "action_verbs": 0.10,
    "quantified_achievements": 0.10,
}

# ─────────────────────────── Resume Sections ───────────────────────────────

RESUME_SECTIONS = [
    "summary", "objective", "profile",
    "experience", "work experience", "professional experience", "employment",
    "projects", "personal projects", "academic projects",
    "skills", "technical skills", "core competencies",
    "education", "academic background",
    "certifications", "certificates", "licenses",
    "achievements", "awards", "honors",
    "publications", "research",
    "volunteer", "extracurricular",
    "languages", "interests", "hobbies",
    "references",
]

# ─────────────────────────── Section Heading Patterns ──────────────────────

SECTION_PATTERNS = {
    "summary": ["summary", "objective", "profile", "about me", "career objective", "professional summary"],
    "experience": ["experience", "work experience", "professional experience", "employment", "work history", "career history"],
    "projects": ["projects", "personal projects", "academic projects", "key projects", "notable projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies", "tools", "proficiencies", "tech stack"],
    "education": ["education", "academic background", "qualifications", "academic qualifications", "degrees"],
    "certifications": ["certifications", "certificates", "licenses", "professional certifications", "credentials"],
    "achievements": ["achievements", "awards", "honors", "accomplishments", "recognitions"],
    "publications": ["publications", "research", "papers", "research papers"],
}

# ─────────────────────────── Action Verbs ──────────────────────────────────

# Weak verbs that should be replaced
WEAK_VERBS = [
    "worked", "helped", "responsible for", "supported", "assisted",
    "involved in", "participated in", "contributed to", "was part of",
    "handled", "managed", "did", "made", "used", "got",
    "tasked with", "in charge of",
]

# Strong action verbs categorized by impact type
STRONG_VERBS = {
    "leadership": ["led", "directed", "orchestrated", "spearheaded", "championed", "pioneered"],
    "creation": ["built", "designed", "developed", "created", "engineered", "architected", "implemented", "launched"],
    "improvement": ["optimized", "enhanced", "streamlined", "accelerated", "improved", "modernized", "revamped", "transformed"],
    "analysis": ["analyzed", "evaluated", "assessed", "investigated", "researched", "diagnosed", "identified"],
    "communication": ["presented", "authored", "published", "communicated", "negotiated", "advocated"],
    "technical": ["programmed", "automated", "integrated", "deployed", "migrated", "configured", "refactored"],
}

# Flattened list of all strong verbs
ALL_STRONG_VERBS = [verb for verbs in STRONG_VERBS.values() for verb in verbs]

# ─────────────────────────── Quantification Indicators ─────────────────────

QUANTIFICATION_INDICATORS = [
    "%", "$", "€", "£", "¥",
    "users", "customers", "clients",
    "revenue", "profit", "savings", "cost",
    "latency", "uptime", "availability",
    "accuracy", "precision", "recall", "f1",
    "requests per second", "rps", "qps",
    "time saved", "hours", "minutes",
    "increased", "decreased", "reduced", "improved",
    "million", "billion", "thousand",
    "team of", "members",
]

# ─────────────────────────── Common Skills Database ────────────────────────

SKILL_CATEGORIES = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "lua",
        "dart", "objective-c", "assembly", "haskell", "elixir", "clojure",
    ],
    "web_frameworks": [
        "react", "angular", "vue", "django", "flask", "fastapi", "express",
        "next.js", "nuxt.js", "spring boot", "rails", "laravel", "asp.net",
        "svelte", "gatsby", "remix",
    ],
    "data_science": [
        "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
        "scikit-learn", "statsmodels", "jupyter", "tableau", "power bi",
    ],
    "machine_learning": [
        "tensorflow", "pytorch", "keras", "xgboost", "lightgbm", "catboost",
        "hugging face", "transformers", "onnx", "mlflow", "wandb",
        "scikit-learn", "opencv", "spacy", "nltk",
    ],
    "deep_learning": [
        "cnn", "rnn", "lstm", "gru", "transformer", "bert", "gpt",
        "attention mechanism", "gan", "autoencoder", "diffusion",
        "reinforcement learning", "transfer learning", "fine-tuning",
    ],
    "cloud_platforms": [
        "aws", "azure", "gcp", "google cloud", "heroku", "digitalocean",
        "vercel", "netlify", "railway", "render",
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "cassandra", "dynamodb", "sqlite", "oracle", "sql server",
        "neo4j", "firebase", "supabase",
    ],
    "devops": [
        "docker", "kubernetes", "jenkins", "github actions", "gitlab ci",
        "terraform", "ansible", "prometheus", "grafana", "nginx",
        "ci/cd", "linux", "bash",
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "slack", "figma", "postman", "swagger", "vs code",
    ],
    "ai_llm": [
        "langchain", "llama index", "openai", "gemini", "claude",
        "rag", "vector database", "faiss", "pinecone", "chromadb",
        "prompt engineering", "fine-tuning", "embeddings",
    ],
}

# Flattened skills list
ALL_SKILLS = [skill for skills in SKILL_CATEGORIES.values() for skill in skills]

# ─────────────────────────── Semantic Skill Mappings ───────────────────────
# Maps related skills for semantic matching

SEMANTIC_SKILL_GROUPS = {
    "deep_learning": ["tensorflow", "pytorch", "keras", "deep learning", "neural network", "cnn", "rnn", "lstm"],
    "machine_learning": ["scikit-learn", "machine learning", "ml", "xgboost", "lightgbm", "random forest", "svm"],
    "nlp": ["spacy", "nltk", "natural language processing", "nlp", "text mining", "sentiment analysis", "ner", "transformers"],
    "databases": ["sql", "mysql", "postgresql", "database", "rdbms", "nosql", "mongodb", "redis"],
    "programming": ["python", "programming", "coding", "software development", "software engineering"],
    "cloud": ["aws", "azure", "gcp", "cloud computing", "cloud", "serverless"],
    "containers": ["docker", "kubernetes", "containerization", "container orchestration", "k8s"],
    "web_dev": ["html", "css", "javascript", "web development", "frontend", "react", "angular", "vue"],
    "data_viz": ["matplotlib", "seaborn", "plotly", "data visualization", "tableau", "power bi", "d3.js"],
    "big_data": ["spark", "hadoop", "kafka", "big data", "data pipeline", "airflow", "etl"],
    "api": ["rest", "rest api", "graphql", "api", "fastapi", "flask", "express", "microservices"],
    "version_control": ["git", "github", "gitlab", "version control", "bitbucket"],
}

# ─────────────────────────── Education Keywords ────────────────────────────

DEGREE_LEVELS = {
    "phd": ["ph.d", "phd", "doctorate", "doctor of philosophy"],
    "masters": ["master", "m.s.", "m.sc", "msc", "m.tech", "mtech", "mba", "m.a.", "ma"],
    "bachelors": ["bachelor", "b.s.", "b.sc", "bsc", "b.tech", "btech", "b.e.", "be", "b.a.", "ba", "bba"],
    "associate": ["associate", "a.s.", "a.a."],
    "diploma": ["diploma", "certificate", "certification"],
}

# ─────────────────────────── File Size Limits ──────────────────────────────

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = [".pdf", ".docx"]

# ─────────────────────────── LLM Settings ──────────────────────────────────

LLM_TEMPERATURE = 0.3
LLM_MAX_OUTPUT_TOKENS = 4096

# ─────────────────────────── UI Configuration ─────────────────────────────

APP_TITLE = "ResumeInsight AI"
APP_SUBTITLE = "AI-Powered Resume Analyzer & ATS Optimizer"
APP_ICON = "🎯"
APP_LAYOUT = "wide"

# Color palette for charts
CHART_COLORS = {
    "primary": "#6C63FF",
    "secondary": "#FF6584",
    "success": "#00C9A7",
    "warning": "#FFC107",
    "danger": "#FF4757",
    "info": "#54A0FF",
    "purple": "#A855F7",
    "teal": "#14B8A6",
    "orange": "#F97316",
    "pink": "#EC4899",
}

CHART_COLOR_SCALE = [
    "#6C63FF", "#00C9A7", "#FF6584", "#FFC107",
    "#54A0FF", "#A855F7", "#14B8A6", "#F97316",
]
