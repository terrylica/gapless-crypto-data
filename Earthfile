VERSION 0.8

# =============================================================================
# Earthfile: Canonical Release-Validation Pipeline
# ADR-0005: Observability-first release workflow
# =============================================================================

# Base Python image with UV
FROM python:3.12-slim
WORKDIR /app

# Install UV package manager
RUN pip install --no-cache-dir uv

# =============================================================================
# DEPENDENCIES
# =============================================================================

deps:
    COPY pyproject.toml uv.lock ./
    RUN uv sync --frozen --no-dev --no-install-project
    SAVE ARTIFACT .venv

deps-dev:
    COPY pyproject.toml uv.lock ./
    RUN uv sync --frozen --no-install-project
    SAVE ARTIFACT .venv

# =============================================================================
# BUILD
# =============================================================================

build:
    FROM +deps-dev
    COPY --dir src tests ./
    COPY pyproject.toml uv.lock README.md CHANGELOG.md LICENSE ./
    RUN uv build
    SAVE ARTIFACT dist AS LOCAL dist

# =============================================================================
# RELEASE STATS (Observability)
# =============================================================================

release-stats:
    ARG --required VERSION
    ARG --required RELEASE_URL
    ARG BUILD_TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    FROM alpine:3.19
    RUN apk add --no-cache jq curl

    # Generate structured release stats JSON
    RUN --no-cache echo "{
        \"package\": \"gapless-crypto-data\",
        \"version\": \"$VERSION\",
        \"release_url\": \"$RELEASE_URL\",
        \"build_time\": \"$BUILD_TIME\",
        \"status\": \"success\"
    }" | jq '.' > /release-stats.json

    RUN cat /release-stats.json
    SAVE ARTIFACT /release-stats.json AS LOCAL logs/release-stats.json

# =============================================================================
# PUSHOVER NOTIFICATION
# =============================================================================

pushover-notify:
    ARG --required VERSION
    ARG --required RELEASE_URL
    ARG --required PUSHOVER_USER_KEY
    ARG --required PUSHOVER_APP_TOKEN
    ARG TITLE="gapless-crypto-data Release"
    ARG PRIORITY=0

    FROM alpine:3.19
    RUN apk add --no-cache curl

    # Send Pushover notification
    RUN --no-cache --secret PUSHOVER_USER_KEY --secret PUSHOVER_APP_TOKEN \
        curl -s \
        --form-string "token=$PUSHOVER_APP_TOKEN" \
        --form-string "user=$PUSHOVER_USER_KEY" \
        --form-string "title=$TITLE" \
        --form-string "message=Version $VERSION released successfully" \
        --form-string "url=$RELEASE_URL" \
        --form-string "url_title=View Release" \
        --form-string "priority=$PRIORITY" \
        https://api.pushover.net/1/messages.json

# =============================================================================
# RELEASE VALIDATION (Full Pipeline)
# =============================================================================

release-validate:
    ARG --required VERSION
    ARG --required RELEASE_URL
    ARG PUSHOVER_USER_KEY
    ARG PUSHOVER_APP_TOKEN

    # Build package
    BUILD +build

    # Generate release stats
    BUILD +release-stats --VERSION=$VERSION --RELEASE_URL=$RELEASE_URL

    # Send notification (if credentials provided)
    IF [ -n "$PUSHOVER_USER_KEY" ] && [ -n "$PUSHOVER_APP_TOKEN" ]
        BUILD +pushover-notify \
            --VERSION=$VERSION \
            --RELEASE_URL=$RELEASE_URL \
            --PUSHOVER_USER_KEY=$PUSHOVER_USER_KEY \
            --PUSHOVER_APP_TOKEN=$PUSHOVER_APP_TOKEN
    END

# =============================================================================
# LOCAL DEVELOPMENT TARGETS
# =============================================================================

# Validate build locally
validate:
    BUILD +build
    RUN echo "Build validation successful"

# Check Earthly syntax
check:
    FROM earthly/earthly:v0.8.15
    COPY Earthfile .
    RUN earthly doc

