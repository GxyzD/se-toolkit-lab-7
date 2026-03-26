FROM harbor.pg.innopolis.university/docker-hub-cache/python:3.14.2-slim-bookworm

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy pyproject.toml and uv.lock first for better caching
COPY bot/pyproject.toml bot/uv.lock /app/

# Install dependencies using uv
RUN uv sync --frozen

# Copy bot code
COPY bot/ /app/

# Copy environment file
COPY .env.docker.secret /app/.env.bot.secret

# Run the bot
CMD ["python", "-m", "bot"]
