#!/usr/bin/env sh

IMAGE_NAME='mongo'
IMAGE_TAG='latest'

CONTAINER_NAME='gb-mongodb'

docker rm -f ${CONTAINER_NAME}

docker run -d --rm --name ${CONTAINER_NAME} \
      -e MONGO_INITDB_ROOT_USERNAME=root \
      -e MONGO_INITDB_ROOT_PASSWORD=password \
      -p 27017:27017 \
      "${IMAGE_NAME}":"${IMAGE_TAG}"
