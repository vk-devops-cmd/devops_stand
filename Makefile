.PHONY: env certs build healthy check start

env:
	cp .env_template .env

certs:
	./gen-certs.sh localhost

build:
	docker compose up -d --build

healthy:
	@echo ""
	@echo "все сервисы healthy"
	@echo ""
	docker compose ps

check:
	@echo ""
	@echo "Проверить приложение через HTTPS (сертификат самоподписанный, поэтому -k)"
	@echo ""
	curl -k https://localhost/

start: env certs build healthy check