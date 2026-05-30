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

echo "==> Cleaning up temporary self-signed cert (if any) ..."
# frontend entrypoint.sh가 nginx 기동용으로 만든 임시 self-signed 인증서를 제거한다.
# (certbot이 관리하지 않는 디렉토리라 그대로 두면 "live directory exists" 오류 발생)
docker compose run --rm --entrypoint sh certbot -c "
  rm -rf /etc/letsencrypt/live/${DOMAIN} \
         /etc/letsencrypt/archive/${DOMAIN} \
         /etc/letsencrypt/renewal/${DOMAIN}.conf
"

echo "==> Requesting certificate for ${DOMAIN} ..."

# certbot 서비스는 자동 갱신 루프를 entrypoint로 갖고 있으므로
# 최초 발급 시에는 --entrypoint 로 certbot 바이너리를 직접 호출한다.
docker compose run --rm --entrypoint certbot certbot certonly \
  --webroot \
  --webroot-path /var/www/certbot \
  --email "${EMAIL}" \
  --agree-tos \
  --no-eff-email \
  -d "${DOMAIN}"

echo "==> Certificate issued. Restarting frontend with SSL ..."
DOMAIN="${DOMAIN}" docker compose up -d --no-deps frontend

echo "==> Done! https://${DOMAIN} is now available."
