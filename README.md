<p align="center">
  <img src="docs/assets/logo.svg" width="120" height="120" alt="My-youtube logo">
</p>

<h1 align="center">My-youtube</h1>

<p align="center">
  <strong>Upload a video, get it transcoded in every resolution, find it by search, watch it.</strong><br>
  A YouTube-like platform in nine containers: a Nuxt front end, a Flask API, a secured
  three-node Elasticsearch cluster, a RabbitMQ queue, an ffmpeg encoder and a mailer.
</p>

<p align="center">
  <a href="#quick-start">Quick start</a> &middot;
  <a href="#how-it-works">How it works</a> &middot;
  <a href="#services">Services</a> &middot;
  <a href="#tech-stack">Tech stack</a> &middot;
  <a href="#documentation">Documentation</a>
</p>

<p align="center">
  <img alt="Python 3.7" src="https://img.shields.io/badge/Python-3.7-3776AB?logo=python&amp;logoColor=white">
  <img alt="Nuxt 2.13" src="https://img.shields.io/badge/Nuxt-2.13-00DC82?logo=nuxtdotjs&amp;logoColor=white">
  <img alt="Elasticsearch 7.8" src="https://img.shields.io/badge/Elasticsearch-7.8-005571?logo=elasticsearch&amp;logoColor=white">
  <img alt="RabbitMQ 3" src="https://img.shields.io/badge/RabbitMQ-3-FF6600?logo=rabbitmq&amp;logoColor=white">
  <img alt="Postgres 12.2" src="https://img.shields.io/badge/Postgres-12.2-4169E1?logo=postgresql&amp;logoColor=white">
  <img alt="Docker Compose" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&amp;logoColor=white">
</p>

---

**My-youtube** was the final step of an ETNA school project (2020-2022): take the JWT API of
[My-api](https://github.com/verovec/My-api) and turn it into a small video platform. Users
register, log in, upload videos, watch them in the quality they choose, search them and comment on
them.

The interesting part is what happens after an upload. The API stores the file, indexes its
metadata in Elasticsearch and publishes a message on RabbitMQ. An encoder worker consumes that
message, runs ffmpeg once per lower resolution down to 240p, registers each output on the API and
asks the mailer to notify the author. The Elasticsearch cluster has three nodes with X-Pack
security and TLS between nodes, which is why the stack needs certificates before it can start.

The repository is archived as it was handed in. The "bonus" list of the original README is now
the [Services](#services) table below.

## Quick start

**Prerequisites:** Docker with Compose, about 4 GB of free memory for the three Elasticsearch
nodes, and on Linux the kernel setting below. Review the passwords in `docker-compose.yml` before
exposing anything.

```sh
git clone https://github.com/verovec/My-youtube.git && cd My-youtube
sudo sysctl -w vm.max_map_count=262144                 # required by Elasticsearch on Linux
rm elasticsearch/certs/bundle.zip                      # the script skips generation when the bundle exists
docker-compose -f elasticsearch/create-certs.yml up    # elasticsearch-certutil writes ca/, es01/, es02/, es03/, kibana/
docker-compose up -d --build                           # the nine services
docker-compose logs -f api encoder                     # wait for the migrations and the queue consumer
```

The front end is on `http://localhost:9982`, the API and its Swagger UI on
`http://localhost:9980`, Adminer on `http://localhost:9981` and Kibana on
`https://localhost:9985` (user `elastic`). The encoding notification needs a mail template of
type `encoding` in the mailer database; see [`docs/development.md`](docs/development.md).

## How it works

```
  Upload        POST /videos with the file; it is saved under uploads/ and a Video row is created
     |
  Index         name, description, pseudo and duration go to the Elasticsearch index "video"
     |
  Queue         a JSON message is published on the RabbitMQ queue "videoCreation"
     |
  Encode        the encoder reads the height with ffprobe, then runs ffmpeg per lower resolution (1080p ... 240p)
     |
  Register      each output is attached with PATCH /video/<id>?format=<res>&file=<path>
     |
  Notify        the encoder calls the mailer, which sends the "encoding" template over SMTP
     |
  Watch         the front plays GET /video/file/<id>?format=<res>; search merges Elasticsearch and Postgres hits
```

## Services

| Service | Image | Host port | Role |
|---------|-------|-----------|------|
| `app` | `node:14.4.0-alpine`, Nuxt 2.13 | 9982 | The front end, dev server with hot reload |
| `api` | `python:3.7-alpine`, Flask | 9980 | JWT API, upload, search, streaming, Swagger UI |
| `encoder` | `python:3.7-alpine` + ffmpeg | none | RabbitMQ consumer transcoding each upload |
| `mailer` | `python:3.7-alpine`, connexion | none (5001 internal) | Mail templates and SMTP sending |
| `rabbitmq` | `rabbitmq:3-management` | none | The `videoCreation` queue |
| `es01`, `es02`, `es03` | `elasticsearch:7.8.0` | none | Three-node cluster, X-Pack security, HTTPS and TLS transport |
| `kibana` | `kibana:7.7.1` | 9985 | HTTPS console on the cluster |
| `database` | `postgres:12.2-alpine` | none | `myproject` (API) and `myprojectmailer` (mailer) databases |
| `adminer` | `adminer:4.7.6` | 9981 | Web client for Postgres |

## Tech stack

| Layer | Tech | Location |
|-------|------|----------|
| Front end | Nuxt 2.13, BootstrapVue 2.15, axios | `app/app/pages/`, `app/app/middleware/` |
| API | Flask, flask-restplus 0.13, PyJWT 1.7, Flask-SQLAlchemy 2.4 | `api/app/controller/`, `api/app/service/` |
| Search | elasticsearch-py 7.8 against `https://es01:9200` | `api/app/service/videos_service.py` |
| Queue | pika 1.1 on RabbitMQ 3, queue `videoCreation` | `api/app/service/videos_service.py`, `encoder/app/consumer.py` |
| Transcoding | ffmpeg, get-video-properties | `encoder/app/consumer.py` |
| Mailer | connexion 2.6, Swagger 2.0 spec, `smtplib` | `ms_mailer/` |
| Certificates | `elasticsearch-certutil` driven by a Compose file | `elasticsearch/create-certs.yml`, `elasticsearch/instances/instances.yml` |
| Packaging | Docker Compose, nine services, five named volumes | `docker-compose.yml` |

Details in [Architecture](docs/architecture.md).

## Documentation

| Topic | Where |
|-------|-------|
| Services, upload pipeline, search, certificates, configuration | [`docs/architecture.md`](docs/architecture.md) |
| Running the stack, the mail template, logs, clean up | [`docs/development.md`](docs/development.md) |
| Every API route with its parameters | [`docs/api.md`](docs/api.md) |
| Everything else | [`docs/`](docs/README.md) |

## Contributing

This is an archived school project and the repository is kept as it was handed in. Issues are
still welcome if you find a mistake in the documentation or want to discuss the design.
