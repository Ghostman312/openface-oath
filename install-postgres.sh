#!/bin/bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgres bitnami/postgresql \
  --namespace postgres-helm \
  --create-namespace \
  --set auth.postgresPassword='StrongPassword' \
  --set primary.persistence.storageClass=do-block-storage \
  --set primary.resources.requests.cpu=250m \
  --set primary.resources.requests.memory=512Mi

#verify
helm list -n postgres-helm
kubectl get pods -n postgres-helm