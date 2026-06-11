rm -rf ./build

TEST_ENABLED="${TEST_ENABLED:-true}"
TEST_COMMAND="${TEST_COMMAND:-python -m pytest -q}"

docker run --rm \
  -v "/$(pwd):/workspace" \
  -w "//workspace" \
  ghcr.io/openfaas/faas-cli build -f stack.yaml \
  --build-arg TEST_ENABLED=${TEST_ENABLED} \
  --build-arg "TEST_COMMAND=${TEST_COMMAND}" \
  --shrinkwrap

ids=$(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-generate-password:1m)
if [ -n "$ids" ]; then docker rm -f $ids; fi
docker rmi ttl.sh/cofrap-mspr-generate-password:1m >/dev/null 2>&1 || true

ids=$(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-generate-2fa:1m)
if [ -n "$ids" ]; then docker rm -f $ids; fi
docker rmi ttl.sh/cofrap-mspr-generate-2fa:1m >/dev/null 2>&1 || true

ids=$(docker ps -a -q --filter ancestor=ttl.sh/cofrap-mspr-authenticate:1m)
if [ -n "$ids" ]; then docker rm -f $ids; fi
docker rmi ttl.sh/cofrap-mspr-authenticate:1m >/dev/null 2>&1 || true

docker build --no-cache --build-arg TEST_ENABLED=${TEST_ENABLED} --build-arg TEST_COMMAND="${TEST_COMMAND}" -t ttl.sh/cofrap-mspr-generate-password:1m ./build/generate-password/
docker build --no-cache --build-arg TEST_ENABLED=${TEST_ENABLED} --build-arg TEST_COMMAND="${TEST_COMMAND}" -t ttl.sh/cofrap-mspr-generate-2fa:1m ./build/generate-2fa/
docker build --no-cache --build-arg TEST_ENABLED=${TEST_ENABLED} --build-arg TEST_COMMAND="${TEST_COMMAND}" -t ttl.sh/cofrap-mspr-authenticate:1m ./build/authenticate/

docker push ttl.sh/cofrap-mspr-generate-password:1m
docker push ttl.sh/cofrap-mspr-generate-2fa:1m
docker push ttl.sh/cofrap-mspr-authenticate:1m

PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

faas-cli deploy -f stack.yaml