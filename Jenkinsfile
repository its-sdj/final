pipeline {
    agent any
    
    environment {
        DOCKER_HUB = "your-dockerhub-username"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm  // This will use the repo configured in Jenkins job
            }
        }
        
        stage('Setup Docker') {
            steps {
                sh '''
                    docker --version || echo "Docker not installed!"
                    docker pull python:3.9-slim
                '''
            }
        }
        
        stage('Build') {
            steps {
                sh 'docker build -t ${DOCKER_HUB}/flask-app:${BUILD_ID} .'
            }
        }
    }
    
    post {
        failure {
            echo "Pipeline failed! Check Docker installation and repository URL."
        }
    }
}
