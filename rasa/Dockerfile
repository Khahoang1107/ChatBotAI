# 🧠 BERT-Enhanced Rasa Dockerfile
FROM rasa/rasa:3.6.20-full

# Set work directory
WORKDIR /app

# 🚀 Install additional dependencies for BERT
USER root

# Install system dependencies for PyTorch and transformers
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies for BERT
RUN pip install --no-cache-dir -r requirements.txt

# Download Vietnamese spaCy model
RUN python -m spacy download vi_core_news_lg

# 🧠 Download and cache PhoBERT model
RUN python -c "from transformers import AutoTokenizer, AutoModel; \
    AutoTokenizer.from_pretrained('vinai/phobert-base'); \
    AutoModel.from_pretrained('vinai/phobert-base')"

# Copy project files
COPY . .

# Create non-root user (user rasa already exists in base image)
RUN chown -R rasa:rasa /app
USER rasa

# Create directories for models and logs
RUN mkdir -p models logs

# Set environment variables for transformers
ENV PYTHONPATH="/app:${PYTHONPATH}"
ENV TRANSFORMERS_CACHE="/app/models/transformers"
ENV HF_HOME="/app/models/transformers"

# Expose ports
EXPOSE 5005

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5005/ || exit 1

# Train and run Rasa with BERT
CMD ["run", "--cors", "*", "--debug"]