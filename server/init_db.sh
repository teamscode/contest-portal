#! /bin/zsh
set -x

if [[ ! -f manage.py ]]; then
    echo "No manage.py, wrong location"
    exit 1
fi

docker rm -f oj-postgres-dev oj-redis-dev
docker run -it -d -e POSTGRES_DB=onlinejudge -e POSTGRES_USER=onlinejudge -e POSTGRES_PASSWORD=onlinejudge -p 127.0.0.1:5432:5432 --name oj-postgres-dev postgres:12-alpine
docker run -it -d -p 127.0.0.1:6379:6379 --name oj-redis-dev redis:6-alpine

sleep 2

if [ "$1" = "--migrate" ]; then
    echo `cat /dev/urandom | head -1 | md5 | head -c 32` > data/config/secret.key
    python3 manage.py migrate
    python3 manage.py inituser --username root --password rootroot --name "TeamsCode Admin" --email exec@teamscode.org --teamname "TeamsCode Admin" --action create_super_admin
fi
