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

HEALTHCHECK --interval=5s --retries=3 CMD python3 /app/deploy/health_check.py

RUN apk add --update --no-cache build-base nginx openssl curl unzip supervisor jpeg-dev zlib-dev postgresql-dev freetype-dev
RUN curl -fsSL https://raw.githubusercontent.com/MikeMirzayanov/testlib/master/testlib.h -o /usr/include/testlib.h
RUN mkdir /app/deploy
COPY server/deploy/requirements.txt /app/deploy/requirements.txt
RUN pip install --no-cache-dir -r /app/deploy/requirements.txt
RUN apk del build-base --purge

COPY server/. .
COPY --from=frontend-build-env /build/dist ./dist

ENTRYPOINT ["sh", "/app/deploy/entrypoint.sh"]
