# Development

## Toolchain

- Docker with Compose. Every service runs in a container; nothing is installed on the host.
- Linux hosts need `vm.max_map_count=262144` for Elasticsearch (`sudo sysctl -w ...`, or a line in
  `/etc/sysctl.conf` to make it permanent). Docker Desktop on macOS already sets it.
- The three Elasticsearch nodes take 512 MB of heap each; give Docker at least 4 GB.

## First start

```sh
rm elasticsearch/certs/bundle.zip                     # otherwise create_certs skips the generation
docker-compose -f elasticsearch/create-certs.yml up   # writes elasticsearch/certs/{ca,es01,es02,es03,kibana}/
docker-compose -f elasticsearch/create-certs.yml down # remove the one-shot container
docker-compose up -d --build                          # build api, mailer, encoder, app; pull the rest
docker-compose logs -f es01                           # wait for "started" and the cluster health
docker-compose logs -f api mailer encoder             # migrations, then the consumer waits on the queue
```

`git status` shows `bundle.zip` as deleted after the first step; do not commit that deletion, the
generated bundle is yours.

## The mail template

The encoder asks the mailer to send the template whose `type` is `encoding`. The table starts
empty, so create it once (the mailer port is not published; use the API container network):

```sh
docker-compose exec api sh -c 'wget -qO- --post-data "{\"type\":\"encoding\",\"subject\":\"Your video is ready\",\"content\":\"Encoding finished.\"}" --header "Content-Type: application/json" http://mailer:5001/mail/'
```

The SMTP account is hardcoded in `ms_mailer/app/core/mail.py`; replace it before expecting a
mail to arrive.

## Recipes

```sh
docker-compose ps                                     # app 9982, api 9980, adminer 9981, kibana 9985
docker-compose logs -f encoder                        # one ffmpeg run per resolution, then the mailer call
docker-compose restart api                            # after a change the reloader missed
docker-compose exec api python /app/manager.py db migrate -m "change"   # new migration (bind-mounted ./migrations)
docker-compose exec api python /app/manager.py db upgrade
docker-compose exec app npm install <package>         # app/app is bind-mounted, package.json is updated
docker-compose down                                   # stop, keep volumes (Postgres, Elasticsearch data, RabbitMQ)
docker-compose down -v                                # stop and delete every named volume
```

## Trying the platform

1. Open `http://localhost:9982`, register, log in.
2. Dashboard, Upload: pick an MP4 (the duration is read with mutagen, which only understands MP4).
3. Watch `docker-compose logs -f encoder` until the resolutions are registered.
4. Open the video page and pick a resolution; the player streams
   `http://localhost:9980/video/file/<id>?format=<res>`.
5. Kibana: `https://localhost:9985`, user `elastic`, password `elasticpwd` (self-signed
   certificate, accept the warning). The index is `video`.

The Swagger UI of the API is at `http://localhost:9980/`.

## Clean up

```sh
docker-compose down -v
rm -rf uploads migrations logs_api app/app/node_modules
rm -rf elasticsearch/certs/ca elasticsearch/certs/es01 elasticsearch/certs/es02 elasticsearch/certs/es03 elasticsearch/certs/kibana
git checkout elasticsearch/certs/bundle.zip
```

## Conventions

- One namespace per resource in `api/app/controller/`, one service per namespace.
- Every handler returns `service_method(...).getResponse()`; the envelope is built by `ApiResponse`.
- The encoder and the mailer are reached by their Compose names (`api`, `mailer`, `rabbitmq`,
  `es01`); the front end is the only piece that talks to `localhost` ports.
