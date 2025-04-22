pipeline {
    agent any

    environment {
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
                    if (isUnix()) {
                        sh '''
                        mkdir -p test-results
                        python3 -m pytest test_dummy.py -v --cov=app --junitxml=test-results/junit.xml
                        '''
                    } else {
                        powershell """
                        mkdir test-results -Force
                        docker run --rm -v ${WORKSPACE}/test-results:/app/test-results \
                            ${IMAGE_NAME}:${IMAGE_TAG} \
                            python3 -m pytest tests/ -v --cov=app --junitxml=test-results/junit.xml
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
                    withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        if (isUnix()) {
                            sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                            sh """
                            docker push ${IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${IMAGE_NAME}:latest
                            """
                        } else {
                            powershell """
                            docker login -u $env:DOCKER_USER -p $env:DOCKER_PASS
                            docker push ${IMAGE_NAME}:${IMAGE_TAG}
                            docker push ${IMAGE_NAME}:latest
                            """
                        }
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
