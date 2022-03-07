# MyYoutube

Augmentez vos limites I/O de fichiers pour Elasticsearch :

```console
sudo sysctl -w vm.max_map_count=262144
```

Créez les certificats Elasticsearch :

```console
docker-compose up -f elasticsearch/create-certs.yml
```

Mettez à jour le fichier `docker-compose.yml` selon vos préférences de configuration puis lancez le service :

```console
docker-compose up -d
```

MyYoutube est disponible au port `9982`

## Bonus

- Elasticsearch for searching a video
- Secure ELK cluster with 3 instances + HTTPS enabled and running
- RabbitMQ queue instance for encoder
- Visualization of videos
- Visualization of videos in different qualities
- Video suggestions
- Listing comments
- Adding comments
