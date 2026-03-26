FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.14.2-slim-bookworm

WORKDIR /app

# Install dependencies directly with pip
RUN pip install --no-cache-dir python-telegram-bot python-dotenv requests

# Copy bot code
COPY bot/ /app/

# Copy environment file
COPY .env.docker.secret /app/.env.bot.secret

# Run the bot
CMD ["python", "-m", "bot"]
