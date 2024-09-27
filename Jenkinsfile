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
                git credentialsId: '56d22ef9-c4c4-4a53-9c64-5312d3e021e2', url: 'https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo', branch: 'master'
            }
        }
    }
}
