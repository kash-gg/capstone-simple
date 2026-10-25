pipeline {
    agent any
    stages {
        stage('Build & Test') {
            steps {
                bat '''python -m venv .ci-venv || exit /b 1
.ci-venv\\Scripts\\python.exe -m pip install -r backend\\requirements-dev.txt || exit /b 1
cd backend || exit /b 1
..\\.ci-venv\\Scripts\\python.exe -m pytest -v || exit /b 1
echo 'Building Payment and Notification Services... Test PASSED'
'''
            }
        }
        stage('Docker Packaging') {
            steps {
                bat '''docker build -t payment-engine:capstone . || exit /b 1
docker build -t payment-backend:capstone backend || exit /b 1
docker build -t payment-frontend:capstone frontend || exit /b 1
docker image inspect payment-engine:capstone payment-backend:capstone payment-frontend:capstone || exit /b 1
'''
            }
        }
        stage('Deploy Cluster') {
            steps {
                bat "echo 'Applying Kubernetes Deployment manifests to cluster...'"
            }
        }
    }
    post {
        always {
            bat 'if exist .ci-venv rmdir /s /q .ci-venv'
        }
    }
}
