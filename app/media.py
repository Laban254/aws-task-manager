from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import boto3
import json
from .db import db
from app.models import Media
from app.utills.logger import setup_logger 

logger = setup_logger(__name__)

media_blueprint = Blueprint('media', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx', 'xlsx'}

def allowed_file(filename):
    """Check if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_s3(file, filename):
    """Upload a file to an S3 bucket and return the file URL."""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )
    try:
        s3_client.upload_fileobj(file, current_app.config['S3_BUCKET'], filename)
        logger.info(f"File uploaded to S3: {filename}")
        return f"https://{current_app.config['S3_BUCKET']}.s3.us-east-2.amazonaws.com/{filename}"
    except Exception as e:
        logger.error(f"Error during file upload: {e}")
        return None

def send_message_to_sqs(media_id, file_url, thumbnail_url=None):
    """Send a message to an SQS queue with media details."""
    sqs_client = boto3.client(
        'sqs',
        aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
        region_name=current_app.config['AWS_REGION']
    )
    
    queue_url = current_app.config['SQS_QUEUE_URL']  
    
    try:
        response = sqs_client.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'media_id': media_id,
                'file_url': file_url,
                'thumbnail_url': thumbnail_url  
            })
        )
        logger.info(f"Message sent to SQS with ID: {response['MessageId']}")
    except Exception as e:
        logger.error(f"Error sending message to SQS: {e}")

@media_blueprint.route('/create', methods=['GET', 'POST'])
def create_media():
    if request.method == 'POST':
        media_name = request.form['media_name']
        description = request.form['description']
        file = request.files.get('file')
        file_url = None

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_url = upload_to_s3(file, filename)
            if not file_url:
                flash('File upload failed. Please try again.', 'danger')
                logger.warning(f"File upload failed for media: {media_name}")
            else:
                media = Media(media_name=media_name, description=description, file_url=file_url)
                try:
                    db.session.add(media)
                    db.session.commit()
                    send_message_to_sqs(media.id, file_url)
                    flash('Media uploaded successfully!', 'success')
                    logger.info(f"Media uploaded successfully: {media_name}")
                except Exception as e:
                    db.session.rollback()
                    flash('Error saving media. Please try again.', 'danger')
                    logger.error(f"Error saving media: {media_name}, Error: {e}")

        return redirect(url_for('media.create_media'))

    media = Media.query.all()
    logger.info("Rendering media creation page with existing media")
    return render_template('dashboard.html', media=media)

@media_blueprint.route('/delete/<int:media_id>', methods=['POST'])
def delete_media(media_id):
    try:
        media = Media.query.get_or_404(media_id)

        if media.file_url:
            filename = media.file_url.split('/')[-1]
            s3_client = boto3.client(
                's3',
                aws_access_key_id=current_app.config['AWS_ACCESS_KEY_ID'],
                aws_secret_access_key=current_app.config['AWS_SECRET_ACCESS_KEY'],
                region_name=current_app.config['AWS_REGION']
            )
            s3_client.delete_object(Bucket=current_app.config['S3_BUCKET'], Key=filename)
            logger.info(f"Deleted file {filename} from S3")

        db.session.delete(media)
        db.session.commit()
        flash('Media deleted successfully!', 'success')
        logger.info(f"Media deleted: {media_id}")

    except Exception as e:
        db.session.rollback()
        flash('Error deleting media. Please try again.', 'danger')
        logger.error(f"Error deleting media {media_id}: {e}")

    return redirect(url_for('auth.dashboard'))
