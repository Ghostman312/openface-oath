docker run --rm \
  -v "/$(pwd):/workspace" \
  -w "//workspace" \
  ghcr.io/openfaas/faas-cli build -f stack.yaml --shrinkwrap

docker rm -f $(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-generate-password:1m) && docker rmi ttl.sh/cofrap-mspr-generate-password:1m
docker rm -f $(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-generate-2fa:1m) && docker rmi ttl.sh/cofrap-mspr-generate-2fa:1m
docker rm -f $(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-authenticate:1m) && docker rmi ttl.sh/cofrap-mspr-authenticate:1m

docker build -t ttl.sh/cofrap-mspr-generate-password:1m ./build/generate-password/
docker build -t ttl.sh/cofrap-mspr-generate-2fa:1m ./build/generate-2fa/
docker build -t ttl.sh/cofrap-mspr-authenticate:1m ./build/authenticate/

docker push ttl.sh/cofrap-mspr-generate-password:1m
docker push ttl.sh/cofrap-mspr-generate-2fa:1m
docker push ttl.sh/cofrap-mspr-authenticate:1m

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

faas-cli deploy -f stack.yaml