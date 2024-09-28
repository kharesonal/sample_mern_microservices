# Sample MERN Application with Microservices

## Description

This repository contains a sample MERN (MongoDB, Express.js, React, Node.js) application structured with microservices architecture. The project demonstrates deploying a full-stack application using AWS services, Docker, Jenkins for CI/CD, and Kubernetes (EKS) for orchestration. It includes infrastructure as code (IaC) using Boto3 and comprehensive monitoring and logging setups.

## Project Steps

The project is divided into the following steps:

1. **Set Up the AWS Environment**-Install and configure AWS CLI and Boto3.

2. **Prepare the MERN Application**-Containerize the MERN application using Docker and Push Docker images to Amazon ECR.

3. **Version Control**-Use AWS CodeCommit for source code management.

4. **Continuous Integration with Jenkins**
   - Set up Jenkins on an EC2 instance.
   - Create Jenkins jobs for building and pushing Docker images.
     
5. **Infrastructure as Code (IaC) with Boto3**-Define infrastructure components using Boto3 scripts.

6. **Deploying Backend Services**-Deploy backend services on EC2 with Auto Scaling Groups.

7. **Set Up Networking**-Configure Elastic Load Balancer and DNS settings.

8. **Deploying Frontend Services**-Deploy frontend services on EC2.

9. **AWS Lambda Deployment**-Create and manage Lambda functions for specific tasks.

10. **Kubernetes (EKS) Deployment**-Create an EKS cluster and deploy applications using Helm.

11. **Monitoring and Logging**-Set up monitoring with CloudWatch and configure logging solutions.

12. **Final Checks**-Validate the deployment to ensure the application is accessible and functional.

## Prerequisites

- AWS CLI and Boto3 installed and configured
- Docker installed
- Helm installed
- Jenkins installed
- Python 3.x
- Git

## Project Execution steps

Step 1: **Set Up the AWS Environment**

1. **Install AWS CLI**
```
pip install awscli
aws configure
```
2. **Install Boto3**
   
`
pip install boto3
`

Step 2.**Prepare the MERN Application**

1. Clone the Repository:

`
 git clone https://github.com/UnpredictablePrashant/SampleMERNwithMicroservices.git
 `
 
2. Containerize the Application:

  - Create Dockerfile for frontend and backend.

4. Build Docker Images:
```
   docker build -t your-backend-image ./backend
   docker build -t your-frontend-image ./frontend
```
Step 3: **Push Docker Images to Amazon ECR**

#**Create repositories**
aws ecr create-repository --repository-name sona-mern-frontendservice
aws ecr create-repository --repository-name sonal-mern-helloservice
aws ecr create-repository --repository-name sonal-mern-profileservice

#**Authenticate Docker to ECR:**

`
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/f8g8h5d4
`

#**build and Push Images:**
```
docker build -t sona-mern-frontendservice .
docker tag sona-mern-frontendservice:latest public.ecr.aws/f8g8h5d4/sona-mern-frontendservice:latest
docker push public.ecr.aws/f8g8h5d4/sona-mern-frontendservice:latest

docker build -t sonal-mern-helloservice .
docker tag sonal-mern-helloservice:latest public.ecr.aws/f8g8h5d4/sonal-mern-helloservice:latest
docker push public.ecr.aws/f8g8h5d4/sonal-mern-helloservice:latest

docker build -t sonal-mern-profileservice .
docker tag sonal-mern-profileservice:latest public.ecr.aws/f8g8h5d4/sonal-mern-profileservice:latest
docker push public.ecr.aws/f8g8h5d4/sonal-mern-profileservice:latest
```
![Screenshot 2024-09-27 162329](https://github.com/user-attachments/assets/a5e5fe12-b602-4621-aa64-1e6f6d931986)
![Screenshot 2024-09-27 162317](https://github.com/user-attachments/assets/86d69fcd-3034-4945-afbb-ca978e2ac922)
![Screenshot 2024-09-27 162304](https://github.com/user-attachments/assets/21143a08-51c2-43b4-9ffa-b348d5ea3e48)


Step 4: **Version Control with AWS CodeCommit**

1.Create a CodeCommit Repository:

`
aws codecommit create-repository --repository-name Sonal-repo
`
2.**Push Source Code**

```
git remote add codecommit https://git-codecommit.ap-northeast-3.amazonaws.com/v1/repos/sonal-repo
git push codecommit main
```

![Screenshot 2024-09-28 224059](https://github.com/user-attachments/assets/f314e729-5193-4c40-99fc-fcae87bb5378)

Step 5: **Continuous Integration with Jenkins**

1. Install Jenkins Plugins:

  - Docker Pipeline
  -  Amazon ECR
  
2. Create Jenkins Jobs:

- Set up jobs to build and push Docker images to ECR.
- Configure triggers for new commits in CodeCommit.

Step 6:**Infrastructure as Code (IaC) with Boto3**

1.**Define Infrastructure:**

Example Python Script: vpc.py

```
import boto3
ec2 = boto3.client('ec2')

# Create a VPC, subnets, and security groups
# Define Auto Scaling Group and launch configurations
```

2.**Deploying Backend Services**

Deploy Backend on EC2 with ASG: asg.py

Example Python Script:
```
import boto3

asg = boto3.client('autoscaling')
# Define launch configuration and auto-scaling group
```

3.**Networking and DNS Setup**

Create Load Balancer: alb.py

Example Python Script:
```
elb = boto3.client('elb')
# Create and configure Elastic Load Balancer
```

Configure DNS:

Use cloudflare DNS service to set up DNS for your application.

4. **Deploying Frontend Services**

Deploy Frontend on EC2: ec2_instance.py

Example Python Script:

import boto3

ec2 = boto3.client('ec2')

#**Launch EC2 instances for the frontend**
AWS implimentation
all the scripts are added in boto3 folder and for managing them there is infra.py script

AWS Lambda Deployment
Backup Database Script:

dblambdabackup.py.py:

import boto3
import pymongo
import datetime

def lambda_handler(event, context):
    # Backup logic



step 10.Monitoring and Logging

 - Set Up Monitoring with CloudWatch:

Step 11. Final Checks

 - Validate the Deployment:
 - Ensure that the MERN application is accessible.
 - Test both frontend and backend functionality.
 - Check monitoring and logging for any issues.

   ![Screenshot 2024-09-26 203116](https://github.com/user-attachments/assets/e7a27d62-664a-4b42-a110-144d766a8987)







  
