# Architecture

My-youtube is a Docker Compose stack of nine services. The API and the mailer are the ones of
[My-api](https://github.com/verovec/My-api), extended with Elasticsearch, RabbitMQ and a
streaming route; the encoder and the Nuxt front end are new.

## Layers

```
app/
  Dockerfile              node:14.4.0-alpine; entrypoint runs npm install then npm run dev
  app/nuxt.config.js      Nuxt 2 universal mode, bootstrap-vue and @nuxtjs/axios modules
  app/pages/              index (listing and search), video, auth/login, auth/register, dashboard, dashboard/upload
  app/middleware/          authentication.js (session in localStorage), user.js, video.js: axios calls to localhost:9980
  app/components/         NavBar
api/
  Dockerfile, entrypoint  python:3.7-alpine; flask-migrate init, migrate, upgrade, then the dev server
  app/routes.py           flask-restplus Api with the namespaces home, auth, user, users, videos, video
  app/controller/         DTOs, parsers and Resource classes
  app/service/            use cases; videos_service.py holds the Elasticsearch and RabbitMQ calls
  app/model/              User, Video, Comment (SQLAlchemy) and JWToken
encoder/
  Dockerfile              python:3.7-alpine with ffmpeg
  entrypoint.sh           waits for rabbitmq:5672 then runs the consumer
  app/consumer.py         pika consumer of the "videoCreation" queue
ms_mailer/
  Dockerfile, entrypoint  flask db init, migrate, upgrade, then flask run on 5001
  init.sql                creates the myproject and myprojectmailer databases in Postgres
  app/swagger/service.yaml the mailer contract (connexion)
  app/core/mail.py        queries and the SMTP send
elasticsearch/
  create-certs.yml        one-shot Compose file running elasticsearch-certutil
  instances/instances.yml the four instances (es01, es02, es03, kibana) and their DNS names
  certs/                  output: bundle.zip, ca/, es01/, es02/, es03/, kibana/ (crt and key files are ignored)
  kibana/config/kibana.yml HTTPS to es01, server TLS with the kibana certificate
docker-compose.yml        database, adminer, es01, es02, es03, kibana, rabbitmq, api, mailer, encoder, app
```

## Services and ports

| Service | Host port | Container port | Depends on |
|---------|-----------|----------------|------------|
| `app` | 9982 | 3000 | |
| `api` | 9980 | 5000 | database, es01, rabbitmq |
| `adminer` | 9981 | 8080 | |
| `kibana` | 9985 (HTTPS) | 5601 | es01 |
| `mailer` | none | 5001 | database |
| `encoder` | none | | rabbitmq |
| `rabbitmq` | none | 5672 (management UI on 15672, not published) | |
| `es01`, `es02`, `es03` | none | 9200, 9300 | |
| `database` | none | 5432 | |

Named volumes: `myapi_database`, `es01`, `es02`, `es03`, `myapi_rabbitmq`. Bind mounts:
`./uploads` is shared by the API and the encoder, `./migrations` and `./logs_api` belong to the
API, `./elasticsearch/certs` is mounted read-only in every Elasticsearch node, Kibana and the API.

## Upload pipeline

1. `POST /videos` (multipart `file`, `name`, optional `description`, header `X-Api-Auth-Token`)
   checks the extension (`mov`, `avi`, `mp4`, `gif`), saves the file under `/uploads` with a
   hashed name and reads its duration with mutagen.
2. The API indexes `{ids, name, description, created_at, user_id, pseudo, duration}` in the
   Elasticsearch index `video` (created on the fly, `verify_certs=False`).
3. The API publishes `{filenameWithoutExtension, filename, extension, video_ids, email}` on the
   RabbitMQ queue `videoCreation` with the default exchange, then saves the `Video` row.
4. The encoder (`consumer.py`) reads the message, finds the source height with
   `get_video_properties` and maps it to the nearest entry of its table: 2160, 1440, 1080, 720,
   480, 360, 240. For every lower resolution it runs
   `ffmpeg -i <source> -c:a copy -s <WxH> <name>_<res>p.mp4` and calls
   `PATCH http://api:5000/video/<ids>?file=<output>&format=<res>`, which stores the path in the
   JSON column `Video.format`.
5. When the last resolution is done it calls
   `POST http://mailer:5001/mail/send_mail?type=encoding&mail_address=<email>`. The mailer looks
   up the template whose `type` is `encoding` and sends it with `smtplib` over STARTTLS to
   `smtp.gmail.com:587`. The Gmail credentials are hardcoded in `ms_mailer/app/core/mail.py`.

The original resolution is never registered in `Video.format`; only the encoded ones are. A video
uploaded in 480p therefore becomes playable at 360p and 240p.

## Search and playback

`GET /videos` accepts `name`, `pseudo` and `duration`. The service runs a wildcard query on the
Elasticsearch index and a `filter_by` query on Postgres, then merges both lists by `ids` so the
Elasticsearch hits come first and nothing is listed twice. `GET /video/<id>` returns the details
of one video, including the `format` map, and `GET /video/file/<id>?format=<res>` streams the
file of that resolution with `send_from_directory`. The front page (`pages/video.vue`) builds
that URL directly.

## Elasticsearch cluster

The three nodes share `cluster.name: es-docker-cluster`, discover each other through
`discovery.seed_hosts` and run with `xpack.security.enabled`, HTTPS on 9200 and TLS on the
transport layer (`verification_mode: certificate`). Each node loads `certificates/<node>/<node>.crt`
and `.key` signed by `certificates/ca/ca.crt`. Kibana speaks HTTPS to `es01` and serves its own
HTTPS with the `kibana` certificate.

`elasticsearch/create-certs.yml` starts one `elasticsearch:7.7.1` container that runs
`bin/elasticsearch-certutil cert --silent --pem --in config/certificates/instances.yml -out
/certs/bundle.zip` and unzips it into `elasticsearch/certs/`. The script only runs when
`bundle.zip` is absent; the repository ships a `bundle.zip`, so delete it first (or unzip it) to
get the `.crt` and `.key` files, which are ignored by git.

Elasticsearch needs `vm.max_map_count=262144` on the Docker host (Linux) and the Compose file
raises the `memlock` ulimit for each node. Each node is capped at 512 MB of heap.

## Data model

| Table | Columns |
|-------|---------|
| `User` | `id`, `ids`, `username`, `pseudo`, `email` (unique), `password` (SHA-256), timestamps |
| `Video` | `id`, `ids`, `name`, `description`, `filename`, `user_ids`, `path`, `duration`, `format` (JSON map resolution to file), timestamps |
| `Comment` | `id`, `ids`, `content`, `user_ids`, `video_ids`, timestamps |
| `Mail` (database `myprojectmailer`) | `id`, `ids`, `type`, `subject`, `content`, timestamps |

Both databases are created by `ms_mailer/init.sql`, mounted in `docker-entrypoint-initdb.d`.

## Configuration

| Variable | Service | Default | Role |
|----------|---------|---------|------|
| `FLASK_SECRET_KEY` | api | `CHANGE ME WITH A SECURE PASSWORD` | Signs the JWT |
| `FLASK_LEVEL`, `LOG_LEVEL` | api, mailer | `dev`, `DEBUG` | Config class and log level |
| `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | api | `database`, `5432`, `myproject`, `myprojectpwd`, `myproject` | API database |
| `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | mailer | `database`, `5432`, `myproject`, `myprojectpwd`, `myprojectmailer` | Mailer database |
| `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` | rabbitmq, api, encoder | `myproject`, `myprojectpwd` | Queue credentials |
| `ELASTIC_PASSWORD` | es01, es02, es03 | `elasticpwd` | Password of the `elastic` user, also hardcoded in the API and `kibana.yml` |
| `ES_JAVA_OPTS` | es01, es02, es03 | `-Xmx512m -Xms512m` | Heap per node |
| `NODE_ENV`, `CHOKIDAR_USEPOLLING` | app | `development`, `true` | Nuxt dev server and file watching in Docker |

The front end calls `http://localhost:9980` from the browser; that host name is hardcoded in
`app/app/middleware/*.js` and `app/app/pages/video.vue`.
