# API

Base URL: `http://localhost:9980`. The Swagger UI is served at `/`.

## Response envelope

Every route answers `{ "error": bool, "message": str, "data": {...} }`. The HTTP code is 200 on
success, 400 on a functional error, 401 on a missing or invalid token, 404 on an unknown route.
Protected routes expect the header `X-Api-Auth-Token: <token>`. Paginated routes accept `page`
(default 1) and `per_page` (default 5, maximum 100) and return `data.pager` with `current` and
`total`.

## Health and auth

| Method | Route | Token | Parameters | Answer |
|--------|-------|-------|------------|--------|
| `GET` | `/home` | no | | `"Everything's up and running"` |
| `POST` | `/auth` | no | JSON `username`, `password` | `data.id`, `data.token`, `data.expires_at` (three hours) |
| `POST` | `/auth/check` | yes | | `data.expires_at`, 401 when invalid |

## Users

| Method | Route | Token | Parameters | Answer |
|--------|-------|-------|------------|--------|
| `POST` | `/user` | no | JSON `username`, `pseudo`, `email`, `password` | 400 when one of the unique fields exists |
| `GET` | `/user/<id>` | yes | | Profile; `email` only on your own |
| `PUT` | `/user/<id>` | yes | JSON `username`, `pseudo`, `email`, `password` | Own profile only |
| `DELETE` | `/user/<id>` | yes | | Own profile only |
| `GET` | `/user/<id>/videos` | no | `page`, `per_page` | Videos of that user |
| `GET` | `/users` | yes | `pseudo`, `page`, `per_page` | Users whose pseudo matches |

## Videos

| Method | Route | Token | Parameters | Answer |
|--------|-------|-------|------------|--------|
| `GET` | `/videos` | no | `page`, `per_page`, `name`, `pseudo`, `duration` | Elasticsearch hits merged with Postgres rows |
| `POST` | `/videos` | yes | multipart `file`, `name`; `description` | Saves the file, indexes it, queues the encoding; returns `data.id` |
| `PUT` | `/videos` | yes | `ids`, `name`, `description` | Updates your own video |
| `DELETE` | `/videos` | yes | `ids` | Deletes your own video |
| `GET` | `/videos/<name>` | no | `page`, `per_page` | Videos with that exact name |
| `GET` | `/videos/<id>/comment` | yes | `page`, `per_page` | Comments of the video |
| `POST` | `/videos/<id>/comment` | yes | `content` | Adds a comment |

Accepted upload extensions: `mov`, `avi`, `mp4`, `gif`. The duration is read with mutagen and
only works on MP4 files.

## Video

| Method | Route | Token | Parameters | Answer |
|--------|-------|-------|------------|--------|
| `GET` | `/video/<id>` | no | | Details of one video, including the `format` map |
| `PATCH` | `/video/<id>` | no | `file`, `format` | Registers an encoded file; called by the encoder |
| `GET` | `/video/file/<id>` | no | `format` (`1080`, `720`, `480`, `360`, `240`...) | The video file of that resolution |

## Mailer (internal, `http://mailer:5001`)

| Method | Route | Purpose |
|--------|-------|---------|
| `GET` | `/mail/` | List templates |
| `POST` | `/mail/` | Create a template: JSON `type`, `subject`, `content` |
| `GET` `PUT` `DELETE` | `/mail/{ids}` | Read, update, delete a template |
| `POST` | `/mail/send_mail?type=&mail_address=` | Send the template of that type; used by the encoder with `type=encoding` |

The contract is `ms_mailer/app/swagger/service.yaml`; connexion serves its Swagger UI at `/ui`.
