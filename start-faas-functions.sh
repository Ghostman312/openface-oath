docker run --rm \
  -v "/$(pwd):/workspace" \
  -w "//workspace" \
  ghcr.io/openfaas/faas-cli build -f stack.yaml --shrinkwrap

docker build -t ttl.sh/cofrap-mspr-generate-password:1m ./build/generate-password/

docker push ttl.sh/cofrap-mspr-generate-password:1m

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

faas-cli deploy -f stack.yaml