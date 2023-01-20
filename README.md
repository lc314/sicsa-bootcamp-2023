<h1>Maintaining and Enhancing Data Products<br>SICSA Bootcamp 2023</h1>
A repository to accompany the 'Maintaining and Enhancing Data Products' session in the SICSA Bootcamp 2023.

This repository contains a selection of free and open-source tools to compose a basic CI/CD pipeline, as well as a dummy project to test them against.

The aim is to introduce learners to CI/CD concepts and to provide them with re-usable tools to put these concepts into practice.

- [Before you begin](#before-you-begin)
  - [Create and activate a python virtual environment](#create-and-activate-a-python-virtual-environment)
  - [Install development and application python packages](#install-development-and-application-python-packages)
  - [Pre-download docker images](#pre-download-docker-images)
- [Dummy application](#dummy-application)
  - [Overview](#overview)
  - [Build it](#build-it)
  - [Run it](#run-it)
  - [Test it](#test-it)
  - [Stop it](#stop-it)
- [Syntax scanning](#syntax-scanning)
  - [Pylint](#pylint)
  - [MyPy](#mypy)
- [Unit testing](#unit-testing)
  - [A note on integration testing](#a-note-on-integration-testing)
  - [Unittest](#unittest)
- [Static Application Security Testing (SAST)](#static-application-security-testing-sast)
  - [Bandit](#bandit)
  - [Checkov](#checkov)
- [Dynamic Application Security Testing (DAST)](#dynamic-application-security-testing-dast)
  - [OWASP ZAP](#owasp-zap)
- [Software Bill-of-Materials (SBOM)](#software-bill-of-materials-sbom)
  - [Syft](#syft)
- [System package vulnerabilities](#system-package-vulnerabilities)
  - [Grype](#grype)
- [Jenkins](#jenkins)
  - [Initial Docker setup](#initial-docker-setup)
  - [Run Jenkins](#run-jenkins)
  - [Initial Jenkins setup](#initial-jenkins-setup)
  - [Create a pipeline](#create-a-pipeline)
  - [Cleanup](#cleanup)

## Before you begin

### Create and activate a python virtual environment
Create a new python virtual environment (Linux/Mac users may need to use `python3` instead of `python`)
``` bash
python -m venv venv
```

Activate it:

Bash:
``` bash
source venv/bin/activate
```

Windows powershell:
``` powershell
.\venv\Scripts\Activate.ps1
```
A dialog will appear asking if you want to run software from an untrusted publisher. Enter either 'R' or 'A' as desired.

### Install development and application python packages
Run the following to install the scanning packages and the required packages for the application itself.

Bash:
``` bash
python -m pip install -r requirements_dev.txt && python -m pip install -r app/requirements.txt
```

Windows powershell:
``` powershell
python -m pip install -r requirements_dev.txt; python -m pip install -r app/requirements.txt
```

### Pre-download docker images
Downloading docker images can take some time, so it is worth running the following command to get the downloads started while you work through the rest of the items.

Bash:
``` bash
docker pull lc314/jenkins-sicsa-bootcamp-2023:latest && docker pull python:latest && docker pull owasp/zap2docker-stable
```

Windows powershell:
``` powershell
docker pull lc314/jenkins-sicsa-bootcamp-2023:latest; docker pull python:latest; docker pull owasp/zap2docker-stable
```

## Dummy application
### Overview
The dummy application is a basic Python API application that runs in a Docker container.

It is designed to be poorly-written and insecure to provide example detections for most scans.

### Build it
``` bash
docker build -t test-app:latest .
```

### Run it
``` bash
docker run --rm --name test-app -p 5678:1234 test-app:latest
```

### Test it
Open a new terminal and run the following to test the liveness of the API:
``` bash
curl http://localhost:5678/liveness
```

Test the application's prediction capabilities
``` bash
curl -X POST localhost:5678/predict -d '{"data": "cheese"}'
```

### Stop it
Either kill the process in the terminal or run the following
``` bash
docker stop test-app
```

## Syntax scanning
Most IDEs will come with out-of-the-box syntax scanning or have plugins that will add/improve that functionality. Despite this, it is still worth adding these scans to an automation pipeline as it's very easy for developers to ignore their IDE's warnings.

### Pylint
Pylint can scan your codebase for certain python errors and suggest styling improvements.

Run the following to check the codebase for syntax errors:
``` python
python -m pylint -E app
```

### MyPy
Static type errors can be scanned for using MyPy.

Run the following to perform a scan of the codebase:
``` python
python -m mypy --ignore-missing-imports --exclude 'venv' .
```

## Unit testing
Unit tests are self-contained tests of precise pieces of functionality. These tests should not make external calls (for example, to databases) and should make no (or few) calls to other functions in the codebase.

Unit test libraries are available for almost all languages (e.g. unittest for Python, testthat for R, JUnit for Java, etc.).

### A note on integration testing
Integration testing differs from unit testing in that its tests are not fully self-contained and often serve to test end-to-end functionality e.g. testing a data pipeline can pull from an remote DB, process the data, and send it to a downstream endpoint.

Beware that these tests often take a long time to run and will put increased load on upstream and downstream sources. If run too frequently, your application may be blacklisted e.g. when querying a public API for data. These tests may be triggered each night/weekend to ensure developers have the results at the start of their day.

### Unittest
Run the application's unit tests:
``` bash
python -m unittest discover -s ./app -p 'test_*.py' -v
```

## Static Application Security Testing (SAST)
SAST techniques scan the codebase and environment for known vulnerabilities. SAST scanners take an 'inside out' approach to scanning, in which the scanner has full access to the codebase and possibly its deployment environment, and they don't require the application/system to be running.

Many SAST tools can be integrated directly into an IDE to scan code as it is being written or manually triggered on the development machine. 

Examples for VSCode include Bandit (Python security) and SonarQube (multi-language security and code quality).

### Bandit
Bandit will scan a codebase for common security issues in python code and generate a report. This report will flag each detection with its severity rank and confidence rank.

Run the following to scan the codebase for all levels of severity and confidence, and fail if anything is detected:
``` python
python -m bandit -r . --exclude ./venv
```

As above, but will only fail if a high severity issue is detected with high/medium confidence:
``` python
python -m bandit -r . -lll -ii --exclude ./venv
```

### Checkov
Checkov scans your codebase's cloud infrastructure files for a variety of bad practices, misconfigurations, and security issues.

Run it using the following:
``` python
checkov --directory . --skip-path venv
```

## Dynamic Application Security Testing (DAST)
DAST techniques test systems by actively attacking a running instance of the application. This is an 'outside in' approach, in which the scanner impersonates an outsider attacking a system they do not have privileged access to.

Always ensure that any DAST tests are performed on isolated systems and that you have permission to run the tests.

### OWASP ZAP
OWASP ZAP is a basic penetration testing tool for web applications.

To run the OWASP ZAP pen tester against your API, first create a docker network for them:
``` bash
docker network create test-app-network
```

Run the API in the network:
``` bash
docker run --rm --name test-app -p 5678:1234 --net test-app-network --network-alias test-app test-app:latest
```

Check the API is running:
``` bash
curl http://localhost:5678/liveness
```

Run the pen test:
``` bash
docker run --rm --net test-app-network owasp/zap2docker-stable zap-baseline.py -t http://test-app:1234/ -I
```

Clean up:
``` bash
docker stop test-app
```

## Software Bill-of-Materials (SBOM)
When presenting applications for review, it can be helpful (or legally required) to be able to present a list of all the software that makes up the application and its deployment environment. This can be then be used to flag components with known vulnerabilities, ensure all software is correctly licenced, and more. Importantly, this artefact can be easily re-used in the future as new software vulnerabilities are discovered.

An example of this is the recent Log4J vulnerability - organisations needed to quickly list all applications under their scope that used this vulnerable library then patch them. Having an up-to-date and easily-accessible SBOM facilitates this process, particularly when compared to having to perform ad-hoc scans of entire architectures.

### Syft
Scan the test application container and generate an SBOM by running:
``` bash
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock --name syft anchore/syft:latest test-app:latest
```

## System package vulnerabilities
An SBOM can be fed into a vulnerability scanner to greatly reduce scan times or outsource the processing.

### Grype
Scan the test application container for vulnerabilities by running:
``` bash
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock --name grype anchore/grype:latest test-app:latest
```

## Jenkins

### Initial Docker setup

Create local directory to hold the jenkins_home:
``` bash
mkdir ~/jenkins_home
```

Create docker network for jenkins:
``` bash
docker network create jenkins
```

### Run Jenkins
Run Jenkins with the following Docker command:
``` bash
docker run --rm -p 8080:8080 -p 50000:50000 --net jenkins --name jenkins -v $HOME/jenkins_home:/var/jenkins_home -v /var/run/docker.sock:/var/run/docker.sock --pull=always lc314/jenkins-sicsa-bootcamp-2023:latest
```
Wait until you see a log message saying "Jenkins is fully up and running"

### Initial Jenkins setup
1. Run the following to get the initial admin password for Jenkins:
    ``` bash
    docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
    ```
2. Open http://localhost:8080 in your browser
3. Insert administrator password, click 'Continue'
4. Click 'Select plugins to install'
5. Click 'None' at the top then click 'Install'
6. Click 'Skip and continue as admin'
7. Ensure that 'Jenkins URL' is http://localhost:8080/ then click 'Save and Finish'
8. Click 'Start using Jenkins'

### Create a pipeline
Click 'New item'
- Name: `sicsa_bootcamp`
- Click 'pipeline'
- Click 'Ok'

__Set the job to prevent parallel builds__

For the purposes of this demo, restrict to one build at a time.
- Tick 'Do not allow concurrent builds'

__Set the job to check the repo for changes every minute__

Scroll to 'Build Triggers'
- Tick 'Poll SCM'
- In 'Schedule' enter `* * * * *`

__Set the job to use a Jenkinsfile from our repo__

Scroll to 'Pipeline' -> 'Definition' -> 'Pipeline script from SCM'

- SCM: `Git`
- Repository URL: `https://github.com/lc314/sicsa-bootcamp-2023.git`
- Branch specifier: `*/main`
- Untick 'lightweight checkout'

Click 'Save'

### Cleanup

Stop the Jenkins container by running the following:
``` bash
docker stop jenkins
```

(optional) Delete your Jenkins home directory if you don't intend to use Jenkins again:
``` bash
rm -R ~/jenkins_home
```

(optional) Delete your Jenkins docker network if you don't intend to use Jenkins again:
``` bash
docker network delete jenkins
```
