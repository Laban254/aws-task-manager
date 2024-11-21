import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os

db = SQLAlchemy()

def test_db_connection(app):
    """Function to test database connection"""
    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful.")
        except Exception as e:
            print(f"Database connection failed: {e}")

def test_s3_connection(app):
    """Function to test S3 connection"""
    AWS_ACCESS_KEY_ID = app.config["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY = app.config["AWS_SECRET_ACCESS_KEY"]
    AWS_REGION = app.config["AWS_REGION"]
    S3_BUCKET_NAME = app.config["S3_BUCKET"]

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    test_file_name = "test_file.txt"
    test_file_content = "This is a test file."

    with open(test_file_name, "w") as file:
        file.write(test_file_content)

    try:
        s3_client.upload_file(test_file_name, S3_BUCKET_NAME, test_file_name)
        print(f"File {test_file_name} successfully uploaded to {S3_BUCKET_NAME}.")
    except FileNotFoundError:
        print(f"The file {test_file_name} was not found.")
    except NoCredentialsError:
        print("No valid AWS credentials found.")
    except PartialCredentialsError:
        print("Incomplete AWS credentials found.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if os.path.exists(test_file_name):
            os.remove(test_file_name)