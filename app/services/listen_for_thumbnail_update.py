import boto3
import json
import threading
from app.db import db
from app.models import Media
from app.utills.logger import setup_logger 

logger = setup_logger(__name__)

def listen_for_thumbnail_update(app):
    """Listen for messages from SQS queue containing thumbnail URLs and update the media record."""
    with app.app_context(): 
        sqs_client = boto3.client(
            'sqs',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
            region_name=app.config['AWS_REGION']
        )
        
        queue_url = app.config['SQS_QUEUE_URL']
        
        while True:
            try:
                response = sqs_client.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=10,
                    VisibilityTimeout=60
                )
                
                if 'Messages' in response:
                    message = response['Messages'][0]
                    body = json.loads(message['Body'])
                    
                    media_id = body.get('media_id')
                    thumbnail_url = body.get('thumbnail_url')
                    
                    media = Media.query.get(media_id)
                    if media:
                        media.thumbnail_url = thumbnail_url
                        try:
                            db.session.commit()
                            logger.info(f"Media updated with thumbnail URL: {thumbnail_url} for media ID: {media_id}")
                        except Exception as e:
                            db.session.rollback()
                            logger.error(f"Error updating media with ID {media_id}: {e}")
                    
                    try:
                        sqs_client.delete_message(
                            QueueUrl=queue_url,
                            ReceiptHandle=message['ReceiptHandle']
                        )
                        logger.info(f"Successfully deleted message from SQS for media ID: {media_id}")
                    except Exception as e:
                        logger.error(f"Error deleting message from SQS for media ID {media_id}: {e}")
            
            except Exception as e:
                logger.error(f"Error processing SQS message: {e}")


def start_sqs_listener(app):
    """Start the SQS listener in a separate thread."""
    listener_thread = threading.Thread(target=listen_for_thumbnail_update, args=(app,))
    listener_thread.daemon = True  
    listener_thread.start()
    logger.info("SQS listener started in background thread.")
