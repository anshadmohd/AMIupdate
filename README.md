# AMIupdate

This Python script automates the process of creating an Amazon Machine Image (AMI) from an EC2 instance, updating a launch template with the latest AMI ID, and sending a notification to Slack upon success or failure.


## Configuration

Replace the following variables in the script with your own values:

- `region`: The AWS region where your EC2 instances and launch templates are located.
- `tag_key`: The EC2 instance tag key to identify the instances.
- `tag_value`: The EC2 instance tag value to filter instances.
- `launch_template_name`: The name of the launch template to be updated.
- `ami_name`: The name to be given to the created AMI.a
- `webhook_url`: The URL of your Slack webhook to receive notifications.

## Running the Script

To run the script, execute the `lambda_handler` function. You can also create an AWS Lambda function and trigger it using an event source, such as CloudWatch Events.


## How It Works

1. The script fetches the specified EC2 instance based on the provided tag.
2. It creates an AMI of the instance and waits for it to become available.
3. The most recent version of the launch template is obtained.
4. The script calculates the next version number and updates the launch template with the new AMI ID.
5. A success or error notification is sent to Slack.

## Slack Notifications

This script sends Slack notifications to the specified webhook URL. Make sure to configure your Slack webhook URL in the `webhook_url` variable.

## Error Handling

In case of any errors during execution, the script will send an error notification to Slack and raise an exception.

