pipeline {
    agent any

    environment {
        AWS_ACCOUNT_ID = '975050024946'
        AWS_REGION = 'ap-northeast-3'
	GIT_REPO = "https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo"
        ECR_REPO_BACKEND_HELLO = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-helloservice"
        ECR_REPO_BACKEND_PROFILE = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sonal-mern-profileservice"
        ECR_REPO_FRONTEND = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/sona-mern-frontendservice"
        DOCKER_IMAGE_TAG = "${env.BUILD_ID}"
        CODECOMMIT_REPO = 'sonal-repo'
        CODECOMMIT_BRANCH = 'master'
    }
// https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${env.GIT_REPO}"
            }
        }

	}
}
