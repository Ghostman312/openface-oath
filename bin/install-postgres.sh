#!/bin/bash

kubectl get sc
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm install postgres bitnami/postgresql \
  --namespace postgres \
  --create-namespace \
  --set auth.postgresPassword='StrongPassword' \
  --set auth.database='cofrap_auth' \
  --set auth.username='cofrap_user' \
  --set auth.password='cofrap_pwd' \
  --set primary.resources.requests.cpu=250m \
  --set primary.resources.requests.memory=512Mi

#verify
helm list -n postgres
kubectl get pods -n postgres