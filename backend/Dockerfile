FROM public.ecr.aws/docker/library/python:3.11-slim

WORKDIR /app

# Install dependencies early for better cache utilisation
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY backend /app

# Make sure logs are sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 