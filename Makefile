TARGET := web
BASE_DIR := /var/www/leadspipe

deploy:
	rsync -avz --no-owner --no-group . $(TARGET):$(BASE_DIR)/ \
		--delete \
		--include dist \
		--exclude .git --exclude-from .gitignore
	ssh -t $(TARGET) cp $(BASE_DIR)/config/leadspipe.service /etc/systemd/system
	ssh -t $(TARGET) systemctl daemon-reload
	ssh -t $(TARGET) systemctl restart leadspipe
	# ssh -t $(TARGET) cp $(BASE_DIR)/config/leadspipe.conf /etc/nginx/sites-enabled/
	# ssh -t $(TARGET) systemctl reload nginx

devserver:
	poetry run uvicorn main:app --reload \
		--ssl-certfile config/certificates.pem \
		--ssl-keyfile config/privatekey.pem \
		--log-level debug

test:
	poetry run python -m doctest -v main.py

clean:
	rm -rf dist/app.* dist/vendor.*

.PHONY: deploy devserver clean
