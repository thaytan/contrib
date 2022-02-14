# Alpine with Chrony
An alpine container with chrony installed and running. The included `chrony.conf` contains a config for an isolated setup as per
https://chrony.tuxfamily.org/doc/2.3/manual.html#Isolated-networks

## build

```
cd dockerfiles
docker build . -t alpine-chrony:3-4.1 -f alpine-x86_64-chrony.Dockerfile
```

## run locally

```
docker run -d                       \
            --name chrony           \
            -p 123:123/udp          \
            --cap-add SYS_NICE      \
            --cap-add SYS_TIME      \
            --cap-add SYS_RESOURCE  \
            alpine-chrony:3-4.1

```

If you want to override the config file

```
docker run -d                       \
            --name chrony           \
            -p 123:123/udp          \
            --cap-add SYS_NICE      \
            --cap-add SYS_TIME      \
            --cap-add SYS_RESOURCE  \
            -v <path_to_chrony.conf>:/etc/chrony/chrony.conf:ro     \
            alpine-chrony:3-4.1

```

## run in docker-compose
```
  chrony:
    image: alpine-chrony:3-4.1
    restart: unless-stopped
    networks:
      - chrony
    ports:
      - 0.0.0.0:123:123/udp
    cap_add:
      - SYS_NICE
      - SYS_TIME
      - SYS_RESOURCE
    volumes:
      - ./config-x86/chrony.conf:/etc/chrony/chrony.conf
```