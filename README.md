# Required Environment Variable

* `API_TOKEN`: Telegram Bot API token
* `DATABASE_URL`: e.g. `sqlite:////tmp/database.sqlite`

# Docker Compose

```sh
# prepare environment
cp .env.example .env
docker compose build
docker compose up
```
