# COFRAP Oath back-end

#### *MSPR TPRE921 - "Gérer un projet de développement serverless selon les principes agile dans un environnement multiculturel"*

## 1. Requirements
- [Docker](https://www.docker.com/) installed and running
- [kubectl](https://kubernetes.io/docs/tasks/tools/#install-kubectl-on-windows) installed
- [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download#Windows) installed
- Ports `8080` and `5432` available

## 2. Install
### 2.A Windows

> All commands below are executed through Git bash. If you haven't already, install [Git for Windows](https://git-scm.com/install/windows)

- Install `faas-cli` :
```console
curl -sLSf https://cli.openfaas.com | sh
```
- Start Minikube with openfaas-profile and Docker template :
```console
minikube start -p openfaas-profile --driver=docker
```
- Install Helm with Winget (the pre-installed Windows package manager) :
```console
winget install Helm.Helm
``` 
- Install OpenFaas with Helm using given script :
```console
./bin/install-openfaas.sh
``` 
- Wait one or two minutes, then forward the 8080 port :
```console
kubectl port-forward svc/gateway -n openfaas 8080:8080
```
- Install PostgresSQL as a Kubernetes pod :
```console
./bin/install-postgres.sh
```
- Pull python3-flask faas template
```console
faas-cli template store pull python3-flask
```
- Start OpenFaas functions :
```console
./bin/start-faas-functions.sh
```

## 3. Available functions

| Function | Base URL | Method | Request body | Successful response body | Error response(s) |
|----------|----------|----------|----------|----------|----------|
| generate-password | http://127.0.0.1:8080/function/generate-password | POST | `{ "username": string }` | `{ "message": "User created successfully.", "password": string, "statusCode": 201 }` | `400` if username is missing. `500` if internal server error |
| generate-2fa | http://127.0.0.1:8080/function/generate-2fa | POST | `{ "username": string }` | `{ "message": "TOTP created successfully.", "totp": string }` | `400` if username is missing. `500` if internal server error |
| authenticate | http://127.0.0.1:8080/function/authenticate | POST | `{ "username": string, "password": string, "totp_code": number }` | `{ "authenticated": true }` | `400` and `{ "authenticated": false, "expired": false }` if username, password or TOTP code are missing, or if any of these are invalid. `401` and `{ "authenticated": false, "expired": true } if password expired. `500` if internal server error |

## 4. Tests

Tests run when using the start-faas-function script during the build phase. However, if you want to run them locally you can do so by using the following script. **Python must be installed on your device**.
```console
./bin/test-functions.sh
```