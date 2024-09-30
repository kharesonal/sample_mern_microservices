pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-3'
        ECR_ACCOUNT_ID = '975050024946'
        FRONTEND_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sona-mern-frontendservice"
        HELLO_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-helloservice"
        PROFILE_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-profileservice"
        AWS_CREDENTIALS_ID = 'AWS-CREDENTIAL' 
        JENKINS_USER_ID = 'sonal'
    }

    stages {
        stage('Checkout') {
            steps {
                git(
                    credentialsId: '56d22ef9-c4c4-4a53-9c64-5312d3e021e2', 
                    url: 'https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo', 
                    branch: 'master'
                )
            }
        }

        stage('Install Docker') { 
            steps {
                script {
                    if (sh(script: "which docker", returnStatus: true) != 0) {
                        sh "sudo apt update"
                        sh "sudo apt install -y docker.io"
                        sh "sudo systemctl start docker"
                        sh "sudo systemctl enable docker"
                    } else {
                        echo "Docker is already installed."
                    }
                }
            }
        }

        
        stage('Login to ECR') {
            steps {
                script {
                    def loginCommand = sh(script: "aws ecr get-login-password --region ${AWS_REGION}", returnStdout: true).trim()
                    sh "echo ${loginCommand} | sudo docker login --username AWS --password-stdin ${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
                }
            }
        }

        stage('Push Frontend Docker Image') {
            steps {
                script {
                    sh "sudo docker tag microfrontend:${env.BUILD_NUMBER} ${FRONTEND_ECR_URI}"
                    sh "sudo docker push ${FRONTEND_ECR_URI}"
                }
            }
        }

        stage('Push Hello Service Docker Image') {
            steps {
                script {
                    sh "sudo docker tag microhello:${env.BUILD_NUMBER} ${HELLO_ECR_URI}"
                    sh "sudo docker push ${HELLO_ECR_URI}"
                }
            }
        }

        stage('Push Profile Service Docker Image') {
            steps {
                script {
                    sh "sudo docker tag microprofile:${env.BUILD_NUMBER} ${PROFILE_ECR_URI}"
                    sh "sudo docker push ${PROFILE_ECR_URI}"
                }
            }
        }
    }

    post {
        success {
            echo "All Docker images pushed successfully by ${env.JENKINS_USER_ID}!"
        }
        failure {
            echo "Build failed!"
        }
    }
}