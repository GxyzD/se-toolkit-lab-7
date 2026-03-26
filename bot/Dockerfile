FROM python:3.11-slim

WORKDIR /app

# Install dependencies directly with pip
COPY bot/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copy bot code
COPY bot/ /app/

CMD ["python", "bot.py"]
