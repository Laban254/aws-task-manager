import logging
import boto3
import os
import time
from flask import current_app

cloudwatch_logs = boto3.client('logs', region_name=os.getenv('AWS_REGION'))
LOG_GROUP = '/aws/flask-app-logs'
LOG_STREAM = 'flask-app-log-stream'

def create_log_stream():
    """Create log stream in CloudWatch if it doesn't exist."""
    try:
        cloudwatch_logs.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
    except cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
        pass  

def send_log_to_cloudwatch(message):
    """Send log to CloudWatch Logs."""
    timestamp = int(round(time.time() * 1000)) 
    log_events = [{
        'timestamp': timestamp,
        'message': message
    }]
    
    try:
        cloudwatch_logs.put_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM,
            logEvents=log_events
        )
    except Exception as e:
        print(f"Error sending log to CloudWatch: {str(e)}")

def setup_logger(name):
    """Set up a logger for Flask app with conditional CloudWatch or local file logging."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if current_app.config['DEBUG']:  
        file_handler = logging.FileHandler(f"{name}.log")
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    else:  
        create_log_stream() 
        handler = logging.StreamHandler()  
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        def cloudwatch_handler(message):
            send_log_to_cloudwatch(message)

        logger.addHandler(cloudwatch_handler)

    return logger

