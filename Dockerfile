# Dockerfile
# Uses multi-stage builds requiring Docker 17.05 or higher
# See https://docs.docker.com/develop/develop-images/multistage-build/

#  Creating a python base with shared dependencies
FROM python:3.13-slim-bookworm AS python-base

# non interactive frontend
ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools
RUN apt-get update && apt-get install --no-install-recommends -y \
    libsqlite3-mod-spatialite \
    binutils \
    libproj-dev \
    gdal-bin && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


ENV PYTHONUNBUFFERED=1 \
    CODE_PATH="/code" \
    VENV_PATH="/code/.venv" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# stage for uv    
FROM python-base AS uv-base
# uv binary form official image
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /uvx /bin/


# Development stage
FROM uv-base AS development

WORKDIR $CODE_PATH

# Copy source code
COPY . $CODE_PATH

# Use development entrypoint
ENTRYPOINT ["/code/docker/entrypoint.dev.sh"]

# Testing stage
FROM uv-base AS testing

WORKDIR $CODE_PATH

# Copy source code
COPY . $CODE_PATH

# Use testing entrypoint
ENTRYPOINT ["/code/docker/entrypoint.test.sh"]

# Production build stage
FROM uv-base AS production-build

WORKDIR $CODE_PATH

COPY pyproject.toml uv.lock ./

# Install all dependencies required for production
RUN uv venv --seed
RUN uv sync --frozen --no-dev --extra production --no-install-project

# Production stage
FROM python-base AS production

WORKDIR $CODE_PATH

COPY --from=production-build $VENV_PATH $VENV_PATH
COPY . $CODE_PATH

ENV PATH="$VENV_PATH/bin:$PATH"

ENTRYPOINT [ "/code/docker/entrypoint.prod.sh"]
