#!/bin/sh
# nginx 시작 전 처리:
# 1. DOMAIN 미설정 시 localhost 사용
# 2. Let's Encrypt 인증서가 없으면 임시 self-signed 생성 (nginx 기동 가능하도록)
# 3. envsubst 로 nginx 템플릿 렌더링 후 nginx 실행

DOMAIN="${DOMAIN:-localhost}"
CERT_DIR="/etc/letsencrypt/live/${DOMAIN}"

if [ ! -f "${CERT_DIR}/fullchain.pem" ]; then
  echo "[entrypoint] No cert found for ${DOMAIN}, generating temporary self-signed cert..."
  mkdir -p "${CERT_DIR}"
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout "${CERT_DIR}/privkey.pem" \
    -out    "${CERT_DIR}/fullchain.pem" \
    -subj   "/CN=${DOMAIN}" 2>/dev/null
  echo "[entrypoint] Temporary cert created. Run init-ssl.sh to get a real cert."
fi

# envsubst: nginx 템플릿에서 $DOMAIN 치환
export DOMAIN
envsubst '${DOMAIN}' \
  < /etc/nginx/templates/default.conf.template \
  > /etc/nginx/conf.d/default.conf

echo "[entrypoint] nginx config rendered for domain: ${DOMAIN}"

# certbot이 인증서를 갱신해도 nginx는 자동으로 다시 읽지 않으므로
# 6시간마다 reload 하여 갱신된 인증서를 반영한다.
( while :; do
    sleep 6h
    nginx -s reload 2>/dev/null && echo "[entrypoint] nginx reloaded (cert refresh)"
  done ) &

exec nginx -g "daemon off;"
