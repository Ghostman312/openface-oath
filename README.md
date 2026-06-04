# COFRAP Oath back-end

#### *MSPR TPRE921 - "Gérer un projet de développement serverless selon les principes agile dans un environnement multiculturel"*

## 1. Requirements
- [Docker](https://www.docker.com/) installed and running
- [kubectl](https://kubernetes.io/docs/tasks/tools/#install-kubectl-on-windows) installed
- [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fwindows%2Fx86-64%2Fstable%2F.exe+download#Windows) installed
- Python3 installed
- Ports `8080` and `5432` avaliable

## 2. Install
### 2.A Windows

> All commands below are executed throught Git bash. If you havent allready, install [Git for Windows](https://git-scm.com/install/windows)

- Install `faas-cli` :
```console
curl -sLSf https://cli.openfaas.com | sh
```
- Start Minikube with openfaas-profile and Docker template :
```console
minikube start -p openfaas-profile
```
- Install Helm with Winget (the pre-install Windows packet manager) :
```console
winget install Helm.Helm
``` 
- Install OpenFaas with Helm using given script :
```console
./install-openfaas.sh
``` 
- Await one or two minutes, the forward the 8080 port :
```console
kubectl port-forward svc/gateway -n openfaas 8080:8080
```
- Install PostgresSQL as a Kubernetes pod :
```console
./install-postgres.sh
```
- Pull python3-flask faas template
```console
faas-cli template store pull python3-flask
```
- Start OpenFaas functions :
```console
./start-faas-functions.sh
```

TODO:
    - Other functions
    - Create multiple clear scripts