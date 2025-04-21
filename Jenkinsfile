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
                    
                    docker.tag("${DOCKER_IMAGE}:${env.BUILD_ID}", "${DOCKER_IMAGE}:latest")
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Run tests with coverage
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
                        docker.push("${DOCKER_IMAGE}:${env.BUILD_ID}")
                        docker.push("${DOCKER_IMAGE}:latest")
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'docker system prune -f || true'
        }
        success {
            slackSend(
                channel: '#builds',
                message: "SUCCESS: ${env.JOB_NAME} ${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
        }
        failure {
            slackSend(
                channel: '#builds',
                message: "FAILED: ${env.JOB_NAME} ${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
        }
    }
}
