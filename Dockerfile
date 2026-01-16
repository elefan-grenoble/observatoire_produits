FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /opt/app

# Copy project files
COPY pyproject.toml .
COPY src ./src

# Install dependencies with uv
RUN uv sync --frozen

# RUN
CMD ["uv", "run", "python", "src/data/make_dataset.py"]
