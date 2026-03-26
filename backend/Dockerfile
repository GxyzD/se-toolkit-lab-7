FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.14.2-slim-bookworm

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv requests

# Copy backend code
COPY backend/ /app/

# Run the backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
