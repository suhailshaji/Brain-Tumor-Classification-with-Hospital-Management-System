import os
import boto3
import random

#S3 Credential 
# S3_BUCKET_NAME =os.getenv('BUCKET_NAME')
# S3_KEY =os.getenv('S3_KEY')
# S3_SECRET_KEY =os.getenv('S3_SECRET_KEY')
# S3_REGION=os.getenv('S3_REGION')
# S3_PATH=os.getenv('S3_PATH')
# S3_PATH_MASK=os.getenv('S3_PATH_MASK')


S3_BUCKET_NAME='hmsdetection'

S3_KEY=''

S3_SECRET_KEY=''

S3_REGION='us-east-2'

S3_PATH='uploads/'


#Boto3 S3 Upload
s3_upload = boto3.client(
    's3',
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET_KEY
)
#Boto3 S3 Fetch
s3_fetch = boto3.resource(
    's3', 
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    region_name=S3_REGION
    )


# Define function to upload image to S3
def upload_to_s3(Image_name):
    print("Starting S3 Function to Upload image")
    # Generate random number for key name
    random_number = random.randint(1000000, 9999999) 
    # Define key name with random number and image name
    key = f'uploads/{random_number}{Image_name.filename}'
    # Upload file to S3
    s3_upload.upload_fileobj(Image_name, S3_BUCKET_NAME, key,ExtraArgs={'ACL': 'public-read','ContentType': "image/png"})
    print(f"Image {key} Uploaded to S3 Completed.....") 
    # Return the S3 URL of the uploaded image
    return key