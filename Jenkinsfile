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
                git credentialsId: 'gitr', url: 'https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo', branch: 'master'
            }
        }
    }
}
