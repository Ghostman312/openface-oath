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

### 4.A Test scenarios

| ID | Scénario | Entrée | Résultat attendu |
|----|----------|--------|------------------|
| T01 | Création d’un mot de passe avec username valide | `{ "username": "testuser" }` | Status `201`, message `User created successfully.`, mot de passe généré de 24 caractères |
| T02 | Mot de passe sans username | `{ "is_expired": false }` | Status `400`, body `Username required.` |
| T03 | Requête vide pour generate-password | `null` | Status `400`, body `Username required.` |
| T04 | Mot de passe généré avec tous les types de caractères | `{ "username": "testuser" }` | Mot de passe contenant au moins une minuscule, une majuscule, un chiffre et un caractère de ponctuation |
| T05 | Mot de passe expiré à la création | `{ "username": "testuser", "is_expired": true }` | Status `201`, mot de passe enregistré avec une date d’expiration à la date courante |
| T06 | Mot de passe non expiré à la création | `{ "username": "testuser", "is_expired": false }` | Status `201`, mot de passe enregistré avec une expiration à 180 jours |
| T07 | Erreur de base de données sur generate-password | `{ "username": "testuser" }` | Status `500`, statut `Error`, détail contenant l’erreur de connexion |
| T08 | Paramètres de connexion PostgreSQL corrects | `{ "username": "testuser" }` avec variables d’environnement DB | Connexion appelée avec `DB_HOST`, `DB_USER`, `DB_PWD`, `DB_NAME` |
| T09 | Création TOTP sans username | `null` | Status `400`, body `Username required.` |
| T10 | Création TOTP avec username valide | `{ "username": "user1" }` | Status `201`, message `TOTP created successfully.`, URI TOTP générée |
| T11 | Erreur de base de données sur generate-2fa | `{ "username": "user1" }` | Status `500`, statut `Error`, détail contenant l’erreur de connexion |
| T12 | Authentification avec username inconnu | `{ "username": "nope" }` | Status `400`, `authenticated: false` |
| T13 | Mot de passe expiré à l’authentification | `{ "username": "user", "password": "p" }` | Status `401`, `expired: true`, message `Password expired. Please renew it.` |
| T14 | Mot de passe invalide à l’authentification | `{ "username": "user", "password": "bad" }` | Status `400`, `authenticated: false` |
| T15 | Code TOTP manquant | `{ "username": "user", "password": "p" }` | Status `400`, message `TOTP code required.` |
| T16 | Code TOTP invalide | `{ "username": "user", "password": "p", "totp_code": "000000" }` | Status `400`, message `Invalid TOTP code.` |
| T17 | Authentification réussie | `{ "username": "user", "password": "p", "totp_code": "123456" }` | Status `200`, `authenticated: true` |
| T18 | Erreur de base de données sur authenticate | `{ "username": "user", "password": "p" }` | Status `500`, statut `Error`, détail contenant l’erreur de connexion |