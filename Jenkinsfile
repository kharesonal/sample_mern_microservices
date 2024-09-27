pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '975050024946'
        AWS_REGION = 'ap-northeast-3'
        ECR_REPO_BACKEND_HELLO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-helloservice"
        ECR_REPO_BACKEND_PROFILE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-profileservice"
        ECR_REPO_FRONTEND = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sona-mern-frontendservice"
        DOCKER_IMAGE_TAG = "${env.BUILD_ID}"
        CODECOMMIT_REPO = 'sonal-repo'
        CODECOMMIT_BRANCH = 'master'
    }
// https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo

    stages {
        stage('Checkout Code from CodeCommit') {
            steps {
                script {
                    // Checkout code from CodeCommit repository
                    sh '''
                    git config --global credential.helper '!aws codecommit credential-helper $@'
                    git config --global credential.UseHttpPath true
                    '''
                    // credentialsId: 'code-commit-credential',
                    git branch: "${CODECOMMIT_BRANCH}",
                        credentialsId: 'code-commit-credential',
                        url: "https://git-codecommit.${AWS_REGION}.amazonaws.com/v1/repos/${CODECOMMIT_REPO}"

                    sh '''
                    ls
                    '''    
                }
            }
        }

        stage('Login to AWS and Docker') {
            steps {
                withCredentials([[
                $class: 'AmazonWebServicesCredentialsBinding',
                credentialsId: 'aws_credentials'  // Your AWS credentials ID
                ]]) { 
                    sh '''
                    aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
                    aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
                    aws configure set region ${AWS_REGION}
        
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO_BACKEND_HELLO}
                    '''
                }
            }
        }
	}
}
