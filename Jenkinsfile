pipeline {

    agent any

    environment {
        GIT_REPO = 'https://github.com/lc314/sicsa-bootcamp-2023.git'
        GIT_BRANCH = 'main'
        APP_IMAGE_NAME = 'test-app:latest'
    }

    stages {
        stage('Pull repo to agent') {
            steps {
                git branch: "$GIT_BRANCH", url: "$GIT_REPO"
            }
        }

        stage('MyPy scan') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh "python3 -m mypy --ignore-missing-imports --exclude 'venv' ."
                }
            }
        }
        
        stage('Bandit scan') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh 'python3 -m bandit -r . -lll -ii'
                }
            }
        }

        stage('Checkov scan') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh 'echo \'### Further information on scan detections can be found by navigating the various "policies" sections here: https://docs.bridgecrew.io/docs\''
                    sh 'checkov --directory . --skip-path venv'
                }
            }
        }

        stage('Docker build') {
            steps {
                sh "sudo docker build -t $APP_IMAGE_NAME ."
            }
        }

        stage('Unit tests') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    // Run all unit tests found in the codebase
                    sh "sudo docker run --rm $APP_IMAGE_NAME python3 -m unittest discover -s . -p 'test_*.py' -v"
                }
            }
        }

        stage('Docker run') {
            steps {
                sh "sudo docker run -d --rm --net jenkins --network-alias jenkins-test --name jenkins-test $APP_IMAGE_NAME"
                // Allow container to start
                sh 'sleep 10'
            }
        }

        stage('Liveness test') {
            steps {
                sh 'curl http://jenkins-test:1234/liveness'
            }
        }

        stage('OWASP ZAP baseline scan') {
            steps {
                sh 'sudo docker run --rm --net jenkins owasp/zap2docker-stable zap-baseline.py -t http://jenkins-test:1234/ -I'
            }
        }

        stage('SBOM - Syft') {
            steps {
                sh "sudo syft $APP_IMAGE_NAME -o json=sbom.json -o table"
            }
        }

        stage('Container vulnerabilities - Grype') {
            steps {
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                    sh 'sudo grype sbom:sbom.json --fail-on critical'
                }
            }
        }
    }

    post {
        always {
            script {
                try {
                    sh 'sudo docker stop jenkins-test'
                } catch (err) {
                    sh 'echo "Tried to stop test container but failed."'
                }
            }
        }
    }
}
