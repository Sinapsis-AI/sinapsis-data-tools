FROM sinapsis-nvidia:base
RUN apt-get update && apt-get install -y ffmpeg python3.10-dev

RUN uv pip install sinapsis-data-tools[all] --extra-index-url https://pypi.sinapsis.tech
WORKDIR /app/.venv