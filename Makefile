docker_container ?= aws-packager

default:
	echo "no target entered"

docker-start:
	docker run --rm --detach --name=$(docker_container) -i --platform linux/amd64 -v ./build:/aws-packager-build --entrypoint /bin/bash public.ecr.aws/lambda/python:3.8

packager:
	docker exec $(docker_container) pip install --target /aws-packager-build -r requirements.txt
	cd build
	zip -r ../pkg.zip .
	cd ../
	zip pkg.zip lambda_functions.py

append-src:
	zip pkg.zip lambda_functions.py

docker-stop:
	docker stop $(docker_container)

upload-lambda-code:
	aws lambda update-function-code --function-name $(function) --profile default --zip-file fileb://pkg.zip

full-workflow: docker-start packager docker-stop upload-lambda-code

append-workflow: append-src upload-lambda-code