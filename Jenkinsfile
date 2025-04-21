pipeline {
    agent any
    
    environment {
        DOCKER_REGISTRY = "docker.io"
        DOCKER_USER = "its-sdj"
        APP_NAME = "final"
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${DOCKER_USER}/${APP_NAME}"
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
                    // Build with test dependencies
                    docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}", 
                        "--build-arg ENV=production " +
                        "--build-arg TEST_DEPS='pytest pytest-cov' .")
                    
                    // Alternative tagging method that doesn't require special permissions
                    sh "docker tag ${DOCKER_IMAGE}:${env.BUILD_ID} ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Create test results directory
                    sh 'mkdir -p test-results'
                    
                    docker.image("${DOCKER_IMAGE}:${env.BUILD_ID}").inside {
                        sh '''
                        python -m pytest tests/ -v --cov=app --junitxml=test-results/junit.xml
                        '''
                    }
                }
            }
            post {
                always {
                    junit 'test-results/*.xml'
                    archiveArtifacts artifacts: 'test-results/**/*.*'
                }
            }
        }

        stage('Push') {
            when {
                branch 'main'
            }
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-hub-credentials') {
                        sh "docker push ${DOCKER_IMAGE}:${env.BUILD_ID}"
                        sh "docker push ${DOCKER_IMAGE}:latest"
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f || true'
            // Basic notification alternative
            echo "Build status: ${currentBuild.result ?: 'SUCCESS'}"
            echo "Build URL: ${env.BUILD_URL}"
        }
    }
}
