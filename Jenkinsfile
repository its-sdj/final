pipeline {
    agent any

    environment {
        VENV_DIR = '/venv'
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
            sh '''
                # Build the Docker image using the custom base image with Python installed
                docker build --build-arg BASE_IMAGE=its-sdj/final:v1 -t its-sdj/final:5 --build-arg ENV=production .
                docker tag its-sdj/final:5 its-sdj/final:latest
            '''
        }
    }
}


        stage('Test') {
    steps {
        script {
            sh '''
                # Use bash to activate the virtual environment and run tests
                /bin/bash -c "source /venv/bin/activate && pytest"
            '''
        }
    }
}

        stage('Push') {
            steps {
                script {
                    // Push Docker image to the registry (if tests pass)
                    sh 'docker push its-sdj/final:latest'
                }
            }
        }

        stage('Post Actions') {
            steps {
                sh 'docker system prune -f'
            }
        }
    }

    post {
        always {
            echo "Build status: ${currentBuild.currentResult}"
            echo "Build URL: ${env.BUILD_URL}"
        }
    }
}
