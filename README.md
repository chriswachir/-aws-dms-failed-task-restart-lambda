# AWS DMS Task Auto-Restart with AWS Lambda

This project is designed to automatically restart failed AWS Database Migration Service (DMS) tasks using AWS Lambda. When a DMS task fails, an SNS notification triggers the Lambda function, which checks the event status and attempts to restart the task if necessary. This setup ensures data replication continuity without manual intervention.

## Overview

This repository contains:
- **Lambda Function**: A Python script that listens for SNS notifications, identifies failed DMS tasks, and restarts them.
- **Configuration**: Instructions to set up the SNS topic, DMS task configurations, Lambda permissions, and required IAM roles.

## Getting Started

### Prerequisites

- **AWS Account** with permissions to create Lambda functions, SNS topics, and DMS tasks.
- **AWS CLI** configured on your machine to deploy the Lambda function.
- **Python 3.x** environment to modify and test the Lambda function code if necessary.

### Setup Instructions

1. **Create an SNS Topic for DMS Notifications**:
   - In the **AWS Management Console**, navigate to **SNS** and create a new topic (e.g., `dms-failure-notifications`).

2. **Configure DMS Event Subscriptions**:
   - Go to **Database Migration Service (DMS)** in the AWS Console.
   - In the **Event Subscriptions** section, create a new subscription:
     - Select the **SNS Topic** you created above.
     - Choose **Event Categories** related to task failures (e.g., `FAILURE`).
     - Specify the DMS tasks you want to monitor for failures.

3. **Create the Lambda Function**:
   - In the **AWS Lambda Console**, create a new function with **Python 3.x** as the runtime.
   - Copy and paste the code from `lambda_function.py` (found in this repository) into the Lambda function editor.
   - Set up the necessary permissions for the Lambda function.

4. **Set Permissions**:
   - Assign an **IAM Role** to the Lambda function with the following policies:
     - **AWSLambdaBasicExecutionRole** for basic Lambda logging to CloudWatch.
     - **AmazonDMSFullAccess** or a custom policy with the following specific permissions:
       - `dms:DescribeReplicationTasks`
       - `dms:StartReplicationTask`
     - **SNS read permissions** (optional) if additional access to SNS is required.

5. **Configure Lambda to Trigger on SNS Messages**:
   - In the Lambda function settings, add an SNS trigger.
   - Select the SNS topic you created earlier (e.g., `dms-failure-notifications`).

### Lambda Script Overview

The Lambda function listens to SNS notifications triggered by DMS events and performs the following steps:

1. Parses the SNS message to determine if a DMS task has failed.
2. Identifies the failed task by its `task_name`.
3. Attempts to restart the task by:
   - **Full-load Tasks**: Restarts using `start-replication`.
   - **CDC/Ongoing Tasks**: Resumes using `resume-processing`.

### Code Structure

```python
def lambda_handler(event, context): 
    # Main function to handle incoming SNS events
    
def restart_dms_task(task_name):
    # Function to describe the DMS task, get its ARN, and restart it
```

### Example Event for Testing

```json
{
  "Records": [
    {
      "Sns": {
        "Message": "{\"Event Message\": \"Replication task has failed.\", \"Identifier Link\": \"arn:aws:dms:...\", \"SourceId\": \"your-task-id\"}"
      }
    }
  ]
}
```

## Testing and Debugging

- **Testing**: You can test the Lambda function directly in the AWS Lambda console using the example event above.
- **Logging**: Logs are available in **CloudWatch** under the Lambda function’s log group, which can help you debug any issues.

