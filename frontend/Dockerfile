FROM python:3.13-slim

LABEL maintainer="https://github.com/lougail"
LABEL description="Docker image for the UC1 project"

WORKDIR /app

COPY frontend/requirements.txt .
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN uv pip install --system --no-cache -r requirements.txt

COPY frontend/ ./frontend/

RUN useradd --create-home uc1
RUN chown -R uc1:uc1 /app
USER uc1

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", "--server.address", "0.0.0.0"]