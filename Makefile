deploy:
	docker build -t kwerty-api . && aws ecr get-login-password  --region us-east-1 | docker login --username AWS --password-stdin 992873260398.dkr.ecr.us-east-1.amazonaws.com && docker tag kwerty-api:latest 992873260398.dkr.ecr.us-east-1.amazonaws.com/kwerty-api && docker push 992873260398.dkr.ecr.us-east-1.amazonaws.com/kwerty-api
