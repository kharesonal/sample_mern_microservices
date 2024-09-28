import boto3
from botocore.exceptions import ClientError
import time

def get_default_vpc_id(ec2_client):
    try:
        response = ec2_client.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': ["default_vpc"]}])
        if response['Vpcs']:
            vpc_id = response['Vpcs'][0]['VpcId']
            print(f"VPC default_vpc already exists. VPC id : {vpc_id}")

        
            response = ec2_client.describe_security_groups(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [vpc_id]},
                    {'Name': 'group-name', 'Values': ['testec2-sg']}
                ]
            )
            if response['SecurityGroups']:
                for sg in response['SecurityGroups']:
                    sg_id = sg['GroupId']
                    print(f"Security group testec2-sg already exists. VPC id : {sg_id}")
                    current_ports = set()
                    
                    for rule in sg['IpPermissions']:
                        from_port = rule.get('FromPort')
                        to_port = rule.get('ToPort')
                        
                        if from_port == to_port:
                            current_ports.add(from_port)
                return vpc_id, sg_id, current_ports
            else:
                return vpc_id, None, set() 
        else:
            return None, None, set()
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None, None, set()

def update_default_security_group(ec2_client, required_ports, current_ports, sg_id):
    try:
        ports_to_add = required_ports - current_ports
        ports_to_remove = current_ports - required_ports
        
        if ports_to_add:
            print(f"Adding ports {ports_to_add} to security group {sg_id}")
            for port in ports_to_add:
                ec2_client.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[{
                        'IpProtocol': 'tcp',
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                    }]
                )
        
        if ports_to_remove:
            print(f"Removing ports {ports_to_remove} from security group {sg_id}")
            for port in ports_to_remove:
                if port is not None: 
                    ec2_client.revoke_security_group_ingress(
                        GroupId=sg_id,
                        IpPermissions=[{
                            'IpProtocol': 'tcp',
                            'FromPort': port,
                            'ToPort': port,
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        }]
                    )
    except ClientError as e:
        print(f"An error occurred: {e}")

def fetch_ami_id():
    try:
        session = boto3.Session(profile_name='profile1', region_name="eu-north-1")
        ec2_client = session.client('ec2')

        response = ec2_client.describe_images(Owners=['099720109477'])

        for image in response['Images']:
            if image['Name'] == "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-20240411":
                image_id = image['ImageId']
                print(f"Image name: {image['Name']} and Image ID is: {image_id}")
                return image_id
    except ClientError as e:
        print(f"An error occurred: {e}")
    return None

def create_key_pair(ec2_client, key_pair_name):
    try:
        existing_key_pairs = ec2_client.describe_key_pairs()
        for existing_key_pair in existing_key_pairs['KeyPairs']:
            if existing_key_pair['KeyName'] == key_pair_name:
                print(f"Key pair {key_pair_name} already exists.")
                return
        key_pair_response = ec2_client.create_key_pair(KeyName=key_pair_name)
        with open(f'{key_pair_name}.pem', 'w') as key_file:
            key_file.write(key_pair_response['KeyMaterial'])
        print(f"Key pair {key_pair_name} created and saved.")
    except ClientError as e:
        print(f"An error occurred: {e}")

def create_security_group(ec2_client, vpc_id):
    try:
        response = ec2_client.create_security_group(
            GroupName='testec2-sg',
            Description='Security group for test EC2 instance',
            VpcId=vpc_id
        )
        security_group_id = response['GroupId']
        print(f"Security Group Created {security_group_id} in VPC {vpc_id}")

        return security_group_id
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

def create_vpc(ec2_client):
    try:
        response = ec2_client.create_vpc(CidrBlock='10.0.0.0/16')
        vpc_id = response['Vpc']['VpcId']
        ec2_client.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': 'default_vpc'}])
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
        ec2_client.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})

        subnet_ids = []
        azs = ['eu-north-1a', 'eu-north-1b'] 
        for i, az in enumerate(azs):
            subnet_response = ec2_client.create_subnet(
                VpcId=vpc_id,
                CidrBlock=f'10.0.{i}.0/24',
                AvailabilityZone=az
            )
            subnet_id = subnet_response['Subnet']['SubnetId']
            subnet_ids.append(subnet_id)
            ec2_client.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': f'default_subnet_{az}'}])

            ec2_client.modify_subnet_attribute(
                SubnetId=subnet_id,
                MapPublicIpOnLaunch={'Value': True}
            )

        igw_response = ec2_client.create_internet_gateway()
        igw_id = igw_response['InternetGateway']['InternetGatewayId']
        ec2_client.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)

        route_table_response = ec2_client.create_route_table(VpcId=vpc_id)
        if 'RouteTable' not in route_table_response:
            print("Failed to create route table.")
            return None, []
        
        route_table_id = route_table_response['RouteTable']['RouteTableId']
        ec2_client.create_route(
            RouteTableId=route_table_id,
            DestinationCidrBlock='0.0.0.0/0',
            GatewayId=igw_id
        )

        for subnet_id in subnet_ids:
            ec2_client.associate_route_table(RouteTableId=route_table_id, SubnetId=subnet_id)

        return vpc_id, subnet_ids
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None, []


def get_subnet_id(ec2_client, vpc_id):
    try:
        response = ec2_client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnets = []
        if response['Subnets']:
            for subnet in response['Subnets']:
                subnets.append(subnet['SubnetId'])
            return subnets 
        else:
            print("No subnets found in the specified VPC.")
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

def check_ec2_instance(ec2_client, servername):

    try:
        response = ec2_client.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': [servername]},
                {'Name': 'instance-state-name', 'Values': ['running']}
            ]
        )

        if 'Reservations' in response:
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    print(f"{servername} Instance Already Present, Instance ID: {instance['InstanceId']}")
                    return instance['InstanceId']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")

def check_mern_ami(ec2_client, ami_name):
    try:
        existing_amis = ec2_client.describe_images(Filters=[{'Name': 'name', 'Values': [ami_name]}])
        if existing_amis['Images']:
            print(f"AMI with name '{ami_name}' already exists. Skipping AMI creation. AMI id : {existing_amis['Images'][0]['ImageId']}")
            return existing_amis['Images'][0]['ImageId']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
def create_ami(ec2_client, instance_id, ami_name):
    try:
        response = ec2_client.create_image(
            InstanceId=instance_id,
            Name=ami_name,
            Description='AMI created from running MERN instance',
            NoReboot=True
        )
        ami_id = response['ImageId']
        print(f"AMI {ami_id} created from instance {instance_id}")
        return ami_id
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
def create_ec2_instance(ec2_client,key_pair_name,sg_id,ami_image_id,user_data_script,subnet_id,servername):
    try:
        instance_response = ec2_client.run_instances(
            ImageId=ami_image_id,
            InstanceType='t3.micro',
            KeyName=key_pair_name,
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': servername
                        }
                    ]
                }
            ],
            SubnetId=subnet_id,
            SecurityGroupIds=[sg_id],
            UserData=user_data_script
        )
        if 'Instances' in instance_response:
            for instance in instance_response['Instances']:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name' and tag['Value'] == servername:
                        instance_id = instance['InstanceId']
                        break
            return instance_id
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")

def check_existing_target_group(elbv2_client, target_group_name):
    try:
        response = elbv2_client.describe_target_groups()
        if response['TargetGroups']:
            for target_group in response['TargetGroups']:
                if target_group['TargetGroupName'] == target_group_name:
                    target_group_arn = target_group['TargetGroupArn']
                    return target_group_arn
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None

def create_target_group_with_instances(elbv2_client, target_group_name, vpc_id, protocol, port, instances):
    try:
        existing_target_group_arn = check_existing_target_group(elbv2_client, target_group_name)
        if existing_target_group_arn:
            print(f"Target group {target_group_name} already exists with ARN: {existing_target_group_arn}")
            return existing_target_group_arn
        else:
            print("Target group with desired name is not present, Creating.....")
        
        response = elbv2_client.create_target_group(
            Name=target_group_name,
            Protocol=protocol,
            Port=port,
            VpcId=vpc_id,
            TargetType='instance',
            HealthCheckProtocol=protocol,
            HealthCheckPort=str(port),
            HealthCheckPath='/',
            HealthCheckIntervalSeconds=30,
            HealthCheckTimeoutSeconds=10,
            HealthyThresholdCount=3,
            UnhealthyThresholdCount=3
        )
        target_group_arn = response['TargetGroups'][0]['TargetGroupArn']
        print(f"Target group {target_group_name} created with ARN: {target_group_arn}")
        
        if instances:
            for instance in instances:
                elbv2_client.register_targets(
                    TargetGroupArn=target_group_arn,
                    Targets=[
                        {
                            'Id': instance
                        }
                    ]
                )
                print(f"Instance {instance} registered with target group {target_group_name}")
        
        return target_group_arn
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None


def check_load_balancer_exists(elb_client, lb_name):
    try: 
        response = elb_client.describe_load_balancers()
        # print(response)
        if response['LoadBalancers']:
            return response['LoadBalancers'][0]['LoadBalancerArn']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None 
    
def create_load_balancer(elb_client, lb_name, subnet_id, sg_id):
    try: 
        response = elb_client.create_load_balancer(
            Name=lb_name,
            Subnets=subnet_id, 
            SecurityGroups=[sg_id],  
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        if response['LoadBalancers']:
            return response['LoadBalancers'][0]['LoadBalancerArn']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred while creating load balancer: {e}")
        return None


def check_listener_exists(elb_client, load_balancer_arn):
    try:
        response = elb_client.describe_listeners(LoadBalancerArn=load_balancer_arn)
        if response['Listeners']:
            return response['Listeners'][0]['ListenerArn']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
def create_listener(elb_client, load_balancer_arn, target_group_arn):
    try:
        response = elb_client.create_listener(
            LoadBalancerArn=load_balancer_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': target_group_arn
                }
            ]
        )
        if response['Listeners']:
            return response['Listeners'][0]['ListenerArn']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None
    
def check_launch_configuration_exists(asg_client, launch_configuration_name):
    try:
        response = asg_client.describe_launch_configurations(
            LaunchConfigurationNames=[launch_configuration_name]
        )
        if response['LaunchConfigurations']:
            print(f"Launch Configuration {launch_configuration_name} already exists.")
            return response['LaunchConfigurations'][0]['LaunchConfigurationName']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred while checking Launch Configuration: {e}")
        return None

def create_launch_configuration(asg_client, launch_configuration_name, ami_id, instance_type, key_name, security_group_id):
    try:
        response = asg_client.create_launch_configuration(
            LaunchConfigurationName=launch_configuration_name,
            ImageId=ami_id,
            InstanceType=instance_type,
            KeyName=key_name,
            SecurityGroups=[security_group_id],
        )
        print(f"Launch Configuration {launch_configuration_name} created successfully.")
        return launch_configuration_name
    except ClientError as e:
        print(f"An error occurred while creating Launch Configuration: {e}")
        return None

def check_auto_scaling_group_exists(asg_client, asg_name):
    try:
        response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])
        if response['AutoScalingGroups']:
            print(f"Auto Scaling Group {asg_name} already exists.")
            return response['AutoScalingGroups'][0]['AutoScalingGroupName']
        else:
            return None
    except ClientError as e:
        print(f"An error occurred while checking ASG: {e}")
        return None

def create_auto_scaling_group(asg_client, asg_name, launch_configuration_name, vpc_id, subnet_ids):
    try:
        response = asg_client.create_auto_scaling_group(
            AutoScalingGroupName=asg_name,
            LaunchConfigurationName=launch_configuration_name,
            MinSize=1,
            MaxSize=2,
            DesiredCapacity=1,
            VPCZoneIdentifier=','.join(subnet_ids),
            Tags=[
                {
                    'Key': 'Name',
                    'Value': asg_name,
                    'PropagateAtLaunch': True
                }
            ]
        )
        print(f"Auto Scaling Group {asg_name} created successfully.")
        return asg_name
    except ClientError as e:
        print(f"An error occurred while creating ASG: {e}")
        return None

def main():
    try:
        required_ports = {22, 3000, 3001, 80, 4411}
        key_pair_name = 'sonal-instance.pem'
        ami_name = 'AMIImageofMernserver'
        lb_name = 'mern-load-balancing'
        asg_name = 'MERNAppASG'
        launch_configuration_name = 'MERNAppLaunchConfiguration'
        instance_type = 't3.micro'
        session = boto3.Session(profile_name='profile1', region_name="eu-north-1")
        ec2_client = session.client('ec2')
        elbv2_client = session.client('elbv2')
        asg_client = session.client('autoscaling')

        vpc_id, sg_id, current_ports = get_default_vpc_id(ec2_client)

        if not vpc_id:
            print("Default VPC not found. Creating...")
            vpc_id = create_vpc(ec2_client)
            sg_id = create_security_group(ec2_client, vpc_id)

        if not sg_id:
            print("Security group not found. Creating...")
            sg_id = create_security_group(ec2_client, vpc_id)

        update_default_security_group(ec2_client, required_ports, current_ports, sg_id)

        with open('./userdata_shell.sh', 'r') as userdata_file:
            user_data_script = userdata_file.read()

        subnet_id = get_subnet_id(ec2_client, vpc_id)

        primary_instance_id = check_ec2_instance(ec2_client, servername='primaryserver')
        if primary_instance_id is None:
            print("Primary server instance not found, creating one...")
            create_key_pair(ec2_client, key_pair_name)
            ami_image_id = fetch_ami_id()
            if ami_image_id is None:
                print("AMI ID not found")
                return
            primary_instance_id = create_ec2_instance(ec2_client, key_pair_name, sg_id, ami_image_id, user_data_script, subnet_id[0], servername='primaryserver')
            if primary_instance_id is not None:
                print(f"Primary server created: {primary_instance_id}")
                print("Waiting for the instance to be up and userdata to execute...")
                time.sleep(420)
                ami_id = create_ami(ec2_client, primary_instance_id, ami_name)
                waiter = ec2_client.get_waiter('image_available')
                print("Waiting for AMI to become available...")
                waiter.wait(ImageIds=[ami_id])
                print(f"AMI {ami_id} is now available.")
        else:
            ami_id = check_mern_ami(ec2_client, ami_name)
            if ami_id is None:
                ami_id = create_ami(ec2_client, primary_instance_id, ami_name)
                waiter = ec2_client.get_waiter('image_available')
                print("Waiting for AMI to become available...")
                waiter.wait(ImageIds=[ami_id])
                print(f"AMI {ami_id} is now available.")

        secondary_instance_id = check_ec2_instance(ec2_client, servername='secondaryserver')
        with open('./userdata_shell_secondary.sh', 'r') as userdata_file:
            user_data_script = userdata_file.read()
        if secondary_instance_id is None:
            print("Secondary server instance not found, creating one...")
            secondary_instance_id = create_ec2_instance(ec2_client, key_pair_name, sg_id, ami_id, user_data_script, subnet_id[0], servername='secondaryserver')
            if secondary_instance_id is not None:
                print(f"Secondary server created: {secondary_instance_id}")
                print("Waiting for the instance to be up and userdata to execute...")
                time.sleep(420)

        target_group_arn = create_target_group_with_instances(elbv2_client, 'MyTargetGroup', vpc_id, 'HTTP', 80, [primary_instance_id, secondary_instance_id])
        if target_group_arn is None:
            print("Failed to create target group.")
            return

        load_balancing_arn = check_load_balancer_exists(elbv2_client, lb_name)
        if load_balancing_arn is None:
            load_balancing_arn = create_load_balancer(elbv2_client, lb_name, subnet_id, sg_id)
        if load_balancing_arn is not None:
            listener_arn = check_listener_exists(elbv2_client, load_balancing_arn)
            if listener_arn is None:
                listener_arn = create_listener(elbv2_client, load_balancing_arn, target_group_arn)
        else:
            print("Failed to create load balancer.")
            return

        launch_configuration_exists = check_launch_configuration_exists(asg_client, launch_configuration_name)
        if launch_configuration_exists is None:
            create_launch_configuration(asg_client, launch_configuration_name, ami_id, instance_type, key_pair_name, sg_id)

        asg_exists = check_auto_scaling_group_exists(asg_client, asg_name)
        if asg_exists is None:
            create_auto_scaling_group(asg_client, asg_name, launch_configuration_name, vpc_id, subnet_id)

    except ClientError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()