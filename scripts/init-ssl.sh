#!/bin/bash
# 최초 SSL 인증서 발급 스크립트
# 사용법: ./scripts/init-ssl.sh yourdomain.com your@email.com
#
# 전제조건:
#   1. 도메인의 A 레코드가 이 서버 IP를 가리키고 있어야 합니다.
#   2. docker compose up -d frontend 가 먼저 실행되어 있어야 합니다 (port 80 오픈).

set -e

DOMAIN="${1:?Usage: $0 <domain> <email>}"
EMAIL="${2:?Usage: $0 <domain> <email>}"

echo "==> Requesting certificate for ${DOMAIN} ..."

docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "${EMAIL}" \
  --agree-tos \
  --no-eff-email \
  -d "${DOMAIN}"

echo "==> Certificate issued. Restarting frontend with SSL ..."
DOMAIN="${DOMAIN}" docker compose up -d --no-deps frontend

echo "==> Done! https://${DOMAIN} is now available."
