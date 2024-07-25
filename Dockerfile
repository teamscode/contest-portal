FROM mirror.gcr.io/library/node:14-alpine AS frontend-build-env

WORKDIR /build
COPY client/. .
COPY .git/. ./.git

RUN apk add git

RUN yarn install --frozen-lockfile && \ 
    yarn build:dll && \
    yarn build


FROM mirror.gcr.io/library/python:3.11-alpine

ENV OJ_ENV production

WORKDIR /app
COPY server/. .

HEALTHCHECK --interval=5s --retries=3 CMD python3 /app/deploy/health_check.py

RUN apk add --update --no-cache build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev && \
    pip install --no-cache-dir -r /app/deploy/requirements.txt && \
    apk del build-base --purge

COPY --from=frontend-build-env /build/dist ./dist

ENTRYPOINT ["sh", "/app/deploy/entrypoint.sh"]