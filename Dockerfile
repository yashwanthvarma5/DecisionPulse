# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements (inline install)
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scipy \
    scikit-learn \
    shap \
    fastapi \
    uvicorn \
    joblib

# Copy project files
COPY src/ src/
COPY models/ models/
COPY data/processed/ data/processed/

# Expose API port
EXPOSE 8000

# Start FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
