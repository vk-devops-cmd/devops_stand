#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-localhost}"
CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/nginx/certs"
DAYS=365

mkdir -p "$CERT_DIR"

if [[ -f "$CERT_DIR/server.crt" && -f "$CERT_DIR/server.key" ]]; then
    echo "Сертификаты уже существуют в $CERT_DIR, пропускаю генерацию."
    echo "Удалите файлы server.crt/server.key, чтобы перегенерировать."
    exit 0
fi

echo "Генерирую self-signed сертификат для домена: $DOMAIN"

openssl req -x509 \
    -nodes \
    -newkey rsa:2048 \
    -days "$DAYS" \
    -keyout "$CERT_DIR/server.key" \
    -out "$CERT_DIR/server.crt" \
    -subj "/C=RU/ST=Local/L=Local/O=DevTest/OU=DevOps/CN=${DOMAIN}" \
    -addext "subjectAltName=DNS:${DOMAIN},DNS:localhost,IP:127.0.0.1"

chmod 644 "$CERT_DIR/server.crt"
chmod 600 "$CERT_DIR/server.key"

echo "Готово:"
echo "  $CERT_DIR/server.crt"
echo "  $CERT_DIR/server.key"
