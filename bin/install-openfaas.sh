#!/bin/bash

helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update
kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml
helm upgrade openfaas --install openfaas/openfaas \
  --namespace openfaas \
  --set functionNamespace=openfaas-fn \
  --set generateBasicAuth=true
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode)
echo "Username: admin"
echo "Password: $PASSWORD"
echo "Use these username and password to access OpenFaas web interface if needed at the address http://127.0.0.1:8080"