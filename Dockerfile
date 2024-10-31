FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# define port and volume
EXPOSE 8080
VOLUME /data
VOLUME /app/.env.prod

# copy files
WORKDIR /app
COPY . /app

# reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# setup
RUN echo "ENVIRONMENT=prod" >> .env
RUN echo "DRIVER=~fastapi+~httpx+~websockets" >> .env
RUN echo "canrot_user_data_path=/data" >> .env
RUN uv sync
RUN http_proxy="http://127.0.0.1:7890" https_proxy="http://127.0.0.1:7890" uv run playwright install

CMD ["uv", "run", "canrotbot"]