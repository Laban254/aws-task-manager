from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")
    COGNITO_POOL_ID = os.getenv("COGNITO_POOL_ID")
    COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
    AWS_REGION = os.getenv("AWS_REGION")
    COGNITO_DOMAIN = os.getenv("COGNITO_DOMAIN")
    REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")

    # PostgreSQL RDS Connection Configuration
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    # SQLAlchemy database URI
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable modification tracking for performance

    # S3-related config entries
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    S3_BUCKET = os.getenv("S3_BUCKET")

    # sqs
    SQS_QUEUE_URL = os.getenv("SQS_QUEUE_URL")
