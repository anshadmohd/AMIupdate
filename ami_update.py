import boto3
import datetime
import http.client
import json

# Replace these variables with your own values
region = "eu-north-1"
tag_key = "Name"
tag_value = "test" 
launch_template_name = "mytemplate"
ami_name = "prod"
webhook_url = ""

ec2 = boto3.client('ec2', region_name=region)

def send_slack_notification(message):
    slack_message = {"text": message}
    conn = http.client.HTTPSConnection("hooks.slack.com")
    conn.request("POST", webhook_url, json.dumps(slack_message), {'Content-Type': 'application/json'})
    response = conn.getresponse()
    conn.close()
    return response.read()

def lambda_handler(event, context):
    try:
        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        ec2_client = boto3.client('ec2', region_name=region)

        instances = ec2_client.describe_instances(Filters=[
            {'Name': f'tag:{tag_key}', 'Values': [tag_value]}
        ])

        if not instances['Reservations']:
            return {
                'statusCode': 404,
                'body': 'No instances found with the specified tag.'
            }

        # Extract the instance ID from the response
        instance_id = instances['Reservations'][0]['Instances'][0]['InstanceId']

        print(f"Creating the AMI of the specified EC2 instance: {instance_id}")
        ami_response = ec2.create_image(
            InstanceId=instance_id,
            Name=f"{ami_name}-{now_date}",
            Description=f"AMI created from instance {instance_id}",
            NoReboot=True
        )

        ami_id = ami_response['ImageId']

        print("Waiting for AMI to become available")
        waiter = ec2.get_waiter('image_available')
        waiter.wait(ImageIds=[ami_id])

        print(f"Created AMI with ID: {ami_id}")

        print("Obtaining the most recent version of the launch template")
        response = ec2.describe_launch_template_versions(
            LaunchTemplateName=launch_template_name
        )

        latest_version = max(response['LaunchTemplateVersions'], key=lambda x: x['VersionNumber'])
        latest_version_number = latest_version['VersionNumber']

        print(f"Recent version of the launch template: {latest_version_number}")

        print("Calculating the next version number by adding 1 to the latest version")
        next_version = latest_version_number + 1

        print("Updating the latest AMI and version details in the launch template")
        ec2.create_launch_template_version(
            LaunchTemplateName=launch_template_name,
            VersionDescription=str(next_version),
            SourceVersion=str(latest_version_number),
            LaunchTemplateData={
                'ImageId': ami_id
            }
        )

        print(f"Latest AMI and version details of the Launch Template updated with AMI ID: {ami_id}")
        
        success_message = f"AMI updated successfully in {now_date}."
        send_slack_notification(success_message)

        return {
            'statusCode': 200,
            'body': success_message
        }
    except Exception as e:
        error_message = f"Lambda function encountered an error: {str(e)}"
        send_slack_notification(error_message)
        raise e
