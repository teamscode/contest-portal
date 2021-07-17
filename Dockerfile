FROM node:lts-buster AS frontend-build-env

WORKDIR /build
COPY ./client/. .

RUN yarn install --frozen-lockfile && \ 
    yarn build:dll && \
    yarn build


FROM python:3.9-alpine

ENV OJ_ENV production

WORKDIR /app
COPY ./server/. .

HEALTHCHECK --interval=5s --retries=3 CMD python2 /app/deploy/health_check.py

RUN apk add --update --no-cache build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev && \
    pip install --no-cache-dir -r /app/deploy/requirements.txt && \
    apk del build-base --purge

COPY --from=frontend-build-env /build/dist ./dist

ENTRYPOINT /app/deploy/entrypoint.sh
