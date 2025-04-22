pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'docker build --build-arg BASE_IMAGE=its-sdj/final:v1 -t its-sdj/final:5 --build-arg ENV=production .'
                    sh 'docker tag its-sdj/final:5 its-sdj/final:latest'
                }
            }
        }

        stage('Test') {
            steps {
                script {
                    // Activate virtual environment and run pytest
                    sh '/bin/bash -c "source /venv/bin/activate && pytest"'
                }
            }
        }

        stage('Push') {
            steps {
                script {
                    // Only push if tests pass
                    sh 'docker push its-sdj/final:latest'
                }
            }
        }

        stage('Post Actions') {
            steps {
                echo 'Build and test completed.'
            }
        }
    }

    post {
        always {
            echo "Build completed"
        }
        failure {
            echo "Build failed"
        }
    }
}
