import json
import boto3

def lambda_handler(event, context):
    """
    Lambda function to monitor AWS DMS task failures and restart the task if it fails.
    The function is triggered by SNS notifications from DMS, which provide details of the event.
    """
    for record in event['Records']:
        # Parse the SNS message from the event record
        message = json.loads(record['Sns']['Message'])
        print("Received message:", message)

        # Extract necessary details from the DMS event message
        dms_event_status = message.get('Event Message', '').split("\n")[0].strip()
        task_id = message.get('Identifier Link', '').strip()  # ARN of the DMS task
        task_name = message.get('SourceId', '').strip()       # ID of the DMS task
        print(f"DMS Event Status: {dms_event_status}")
        print(f"Task ID: {task_id}")
        print(f"Task name: {task_name}")

        # Check if the event status indicates a task failure
        if dms_event_status == 'Replication task has failed.' and task_id and task_name:
            print("Restarting the failed DMS task...")
            restart_dms_task(task_name)
        else:
            print("Event does not indicate a failed DMS task. Skipping to the next record.")

def restart_dms_task(task_name):
    """
    Attempts to restart the specified DMS task by looking up its ARN
    and then choosing the appropriate restart type based on task configuration.
    """
    # Initialize the DMS client
    dms_client = boto3.client('dms')

    # Set up filters to locate the DMS task by its name
    filters_dict = {'Name': 'replication-task-id', 'Values': [task_name]}
    
    try:
        # Describe the DMS task to get details including its ARN
        response = dms_client.describe_replication_tasks(Filters=[filters_dict])
        
        # Ensure the task was found
        if 'ReplicationTasks' in response and response['ReplicationTasks']:
            task_arn = response['ReplicationTasks'][0]['ReplicationTaskArn']

            # Determine the restart type based on the task's migration type
            if response['ReplicationTasks'][0]['MigrationType'] == 'full-load':
                # For full-load tasks, we restart using 'start-replication'
                start_type = 'start-replication'
            else:
                # For CDC (ongoing) tasks, we use 'resume-processing'
                start_type = 'resume-processing'

            # Attempt to restart the task
            try:
                dms_client.start_replication_task(
                    ReplicationTaskArn=task_arn,
                    StartReplicationTaskType=start_type
                )
                print(f"Successfully restarted DMS task: {task_name}")
            except Exception as e:
                print(f"Error restarting DMS task {task_name}: {e}")
        else:
            print(f"DMS task '{task_name}' not found.")
    
    except Exception as e:
        print(f"Error describing DMS task {task_name}: {e}")
