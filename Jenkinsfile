pipeline {
    agent any

    environment {
        AWS_REGION = 'ap-northeast-2'
        ECR_ACCOUNT_ID = '975050024946'
        FRONTEND_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/microfrontend:latest"
        HELLO_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/microhello:latest"
        PROFILE_ECR_URI = "${ECR_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/microprofile:latest"
        AWS_CREDENTIALS_ID = 'gani' 
        JENKINS_USER_ID = 'jenkins'
    }

    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'gitr', url: 'https://git-codecommit.ap-northeast-2.amazonaws.com/v1/repos/micromern', branch: 'main'
            }
        }
    }
}
