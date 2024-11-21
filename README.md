# 🎥 **Media Upload, Metadata Storage & Thumbnail Generation**

This project implements a web application that allows users to upload media files (images), along with titles and descriptions. The application integrates with AWS services for authentication, media storage, and automated thumbnail generation. The backend is built using Flask, and AWS RDS (PostgreSQL) is used to store media metadata. AWS S3 is used for media storage, while AWS Lambda processes the images to generate thumbnails upon receiving notifications from SQS.

----------

## 🚀 **Features**

### 🔒 **User Authentication:**

-   Secure login and signup via **AWS Cognito**.
-   Session tokens are stored for authenticated users.

### 🖼️ **Media Upload:**

-   Users can upload media with a title and description.
-   Media files (images) are stored in **AWS S3**, and metadata (title, description, file URL) is saved in **AWS RDS (PostgreSQL)**.

### 🛠️ **Thumbnail Generation:**

-   An **AWS Lambda** function listens to **SQS** for new media uploads.
-   The Lambda function processes the images, generates thumbnails, and stores them back in **AWS S3**.

### 🔄 **Real-Time Updates:**

-   The **Flask app** listens for **SQS** messages.
-   It updates the media record with the generated thumbnail URL.



----------

## 💻 **Technologies Used**

-   **Backend:** Python, Flask
-   **Authentication:** AWS Cognito
-   **Cloud Services:** AWS S3, AWS Lambda, AWS SQS, AWS RDS (PostgreSQL)
-   **Frontend:** HTML, CSS, JavaScript, Bootstrap
