_installed = False

def _install_packages(*packages):
    global _installed
    if not _installed:
        import os
        import sys
        import time
        _started = time.time()
        os.system("mkdir -p /tmp/packages")
        _packages = " ".join(f"'{p}'" for p in packages)
        os.system(f"{sys.executable} -m pip freeze --no-cache-dir")
        os.system(
            f"{sys.executable} -m pip install "
            f"--no-cache-dir --target /tmp/packages "
            f"--only-binary :all: --no-color "
            f"--no-warn-script-location {_packages}")
        sys.path.insert(0, "/tmp/packages")
        _installed = True
        _ended = time.time()

_install_packages("Pillow")

import json
import boto3
from PIL import Image
from io import BytesIO
import os

def lambda_handler(event, context):
    """Process messages from an SQS queue."""
    try:
        s3_bucket = os.environ.get('S3_BUCKET')
        sqs_queue_url = os.environ.get('SQS_QUEUE_URL')
        
        if not s3_bucket or not sqs_queue_url:
            raise EnvironmentError("Environment variables S3_BUCKET or SQS_QUEUE_URL are not set.")

        for record in event['Records']:
            body = json.loads(record['body'])
            file_url = body.get('file_url')
            media_id = body.get('media_id') 
            thumbnail_url = body.get('thumbnail_url')  
            
            # Download the image from S3
            s3_client = boto3.client('s3')
            file_key = file_url.split("/")[-1]
            
            try:
                image_obj = s3_client.get_object(Bucket=s3_bucket, Key=file_key)
                image_data = image_obj['Body'].read()
            except Exception as e:
                raise Exception(f"Error fetching image from S3: {e}")
            
            # Ensure the image size is within the Lambda /tmp storage limits
            if len(image_data) > 512 * 1024 * 1024:  # 512 MB limit
                raise Exception(f"Image exceeds the maximum allowed size of 512 MB: {len(image_data)} bytes.")
            
            try:
                image = Image.open(BytesIO(image_data))
                supported_formats = ['JPEG', 'PNG', 'GIF', 'BMP']
                if image.format not in supported_formats:
                    raise Exception(f"Unsupported image format: {image.format}. Supported formats: {', '.join(supported_formats)}")
            except Exception as e:
                raise Exception(f"Error processing image: {e}")
            
            image.thumbnail((100, 100))  
            
            # Save the thumbnail to S3
            thumbnail_key = f"thumbnails/{file_key}"
            thumbnail_image = BytesIO()
            image.save(thumbnail_image, format="PNG")
            thumbnail_image.seek(0)
            
            s3_client.put_object(Bucket=s3_bucket, Key=thumbnail_key, Body=thumbnail_image)
            
            thumbnail_url = f"https://{s3_bucket}.s3.amazonaws.com/{thumbnail_key}"
            
            sqs_client = boto3.client('sqs')
            
            message_body = {
                'media_id': media_id,  
                'thumbnail_url': thumbnail_url
            }
            
            response = sqs_client.send_message(
                QueueUrl=sqs_queue_url,
                MessageBody=json.dumps(message_body)
            )
            
    except Exception as e:
        raise e  

    return {
        'statusCode': 200,
        'body': json.dumps('Processing complete')
    }
