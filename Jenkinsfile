pipeline {
    agent any
    environment {
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
        IMAGE_NAME = 'its-sdj/final'
        IMAGE_TAG = '5'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Build') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} \
                            --build-arg ENV=production .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        """
                    } else {
                        powershell """
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} \
                            --build-arg ENV=production .
                        docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }
        stage('Test') {
            steps {
                script {
                    sh 'mkdir -p test-results'
                    if (isUnix()) {
                        withDockerContainer(image: "${IMAGE_NAME}:${IMAGE_TAG}", args: '-u root') {
                            sh 'python -m pytest tests/ -v --cov=app --junitxml=test-results/junit.xml'
                        }
                    } else {
                        powershell """
                        mkdir test-results -Force
                        docker run --rm -v ${WORKSPACE}/test-results:/app/test-results \
                            ${IMAGE_NAME}:${IMAGE_TAG} \
                            python -m pytest tests/ -v --cov=app --junitxml=test-results/junit.xml
                        """
                    }
                }
            }
            post {
                always {
                    junit 'test-results/junit.xml'
                }
            }
        }
        stage('Push') {
            steps {
                script {
                    if (isUnix()) {
                        sh 'echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin'
                        sh """
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                        """
                    } else {
                        powershell """
                        docker login -u $env:DOCKERHUB_CREDENTIALS_USR -p $env:DOCKERHUB_CREDENTIALS_PSW
                        docker push ${IMAGE_NAME}:${IMAGE_TAG}
                        docker push ${IMAGE_NAME}:latest
                        """
                    }
                }
            }
        }
    }
    post {
        always {
            node('') {
                sh 'docker system prune -f'
            }
        }
        success {
            echo 'Build status: SUCCESS'
        }
        failure {
            echo 'Build status: FAILURE'
            echo "Build URL: ${env.BUILD_URL}"
        }
    }
}
