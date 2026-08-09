#!/bin/bash
set -euo pipefail

# Cài và khởi động Docker
dnf install -y docker
systemctl enable --now docker

# Cài Docker Compose plugin
mkdir -p /usr/local/lib/docker/cli-plugins

curl -fSL \
  https://github.com/docker/compose/releases/download/v5.1.2/docker-compose-linux-x86_64 \
  -o /usr/local/lib/docker/cli-plugins/docker-compose

chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Tạo thư mục và Docker network cho Caro
mkdir -p /opt/caro

docker network inspect caro-network >/dev/null 2>&1 \
  || docker network create caro-network

# EC2 dùng CaroWebEC2Role để đăng nhập ECR
aws ecr get-login-password \
  --region ap-southeast-1 \
  | docker login \
      --username AWS \
      --password-stdin \
      727165267644.dkr.ecr.ap-southeast-1.amazonaws.com

# Tạo cấu hình Compose
cat > /opt/caro/compose.yaml <<'COMPOSE'
services:
  api:
    image: 727165267644.dkr.ecr.ap-southeast-1.amazonaws.com/caro-game-api:v1
    container_name: caro-api-service
    restart: unless-stopped
    ports:
      - "127.0.0.1:8000:8000"
    networks:
      - caro-network

  web:
    image: 727165267644.dkr.ecr.ap-southeast-1.amazonaws.com/caro-game-web:v1
    container_name: caro-web
    restart: unless-stopped
    depends_on:
      - api
    ports:
      - "80:80"
    networks:
      - caro-network

networks:
  caro-network:
    external: true
COMPOSE

# Tải image và chạy ứng dụng
docker compose -f /opt/caro/compose.yaml pull
docker compose -f /opt/caro/compose.yaml up -d