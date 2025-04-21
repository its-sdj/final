pipeline {
    agent any
    
    environment {
        // Customize these values:
        DOCKER_REGISTRY = "docker.io"  // Change to your registry (e.g., ghcr.io for GitHub)
        DOCKER_USER = "its-sdj"        // Your Docker Hub/registry username
        APP_NAME = "final"             // Your repository name
        DOCKER_IMAGE = "${DOCKER_REGISTRY}/${DOCKER_USER}/${APP_NAME}"
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '5'))
    }

    stages {
        // Stage 1: Checkout code
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/main']],
                    extensions: [[$class: 'CleanBeforeCheckout']],
                    userRemoteConfigs: [[
                        url: 'https://github.com/its-sdj/final.git'
                    ]]
                ])
                sh 'ls -la'  // Verify files
            }
        }

        // Stage 2: Build Docker image
        stage('Build') {
            steps {
                script {
                    // Build with cache and tags
                    docker.build("${DOCKER_IMAGE}:${env.BUILD_ID}", "--build-arg ENV=production .")
                    
                    // Additional tag for 'latest'
                    sh """
                    docker tag ${DOCKER_IMAGE}:${env.BUILD_ID} ${DOCKER_IMAGE}:latest
                    """
                }
            }
        }

        // Stage 3: Run tests inside container
        stage('Test') {
            steps {
                script {
                    docker.image("${DOCKER_IMAGE}:${env.BUILD_ID}").inside('-e FLASK_ENV=test') {
                        sh '''
                        python -m pytest tests/ -v
                        python app.py &  # Start Flask app
                        sleep 5  # Wait for app to start
                        curl http://localhost:5000/health
                        '''
                    }
                }
            }
        }

        // Stage 4: Push to registry
        stage('Push') {
            steps {
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${env.BUILD_ID}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        // Stage 5: Deploy (Example for AWS ECS)
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    sh """
                    # Example AWS ECS deploy (customize as needed)
                    aws ecs update-service \
                        --cluster your-cluster \
                        --service your-service \
                        --force-new-deployment
                    """
                }
            }
        }
    }

    post {
        always {
            // Clean up Docker
            sh 'docker system prune -f || true'
            
            // Archive test reports
            junit '**/test-reports/*.xml'
            
            // Notifications
            slackSend(
                channel: '#your-channel',
                message: "Pipeline ${currentBuild.result}: ${env.JOB_NAME} #${env.BUILD_NUMBER}\n${env.BUILD_URL}"
            )
        }
        
        success {
            archiveArtifacts artifacts: '**/app.py,**/Dockerfile'
        }
        
        failure {
            mail to: 'your-email@example.com',
                 subject: "FAILED: ${env.JOB_NAME}",
                 body: "Check ${env.BUILD_URL}console"
        }
    }
}
