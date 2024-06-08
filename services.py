from PIL import Image, ImageEnhance, ImageFilter
import cv2
import boto3
import os
from datetime import datetime
import re

class DocumentProcessingService:
    def __init__(self, aws_access_key_id, aws_secret_access_key, region_name, bucket_name):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )
        self.textract_client = boto3.client(
            "textract",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=region_name,
        )

    def download_image_from_s3(self, document_key):
        image_path = f"/tmp/{document_key}"
        self.s3_client.download_file(self.bucket_name, document_key, image_path)
        return image_path

    def upload_image_to_s3(self, processed_image_path, processed_image_key):
        self.s3_client.upload_file(processed_image_path, self.bucket_name, processed_image_key)
    
    def process_image(self, image_path, document_key):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Failed to read image at {image_path}")
            return None

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Crop unnecessary parts (simple example: find contours and crop to bounding box)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cropped_image = gray
        if contours:
            # Consider finding the largest contour or a more sophisticated method to include all relevant parts
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            cropped_image = gray[y:y+h, x:x+w]
        else:
            cropped_image = gray  # No cropping if no contours found

        # Convert to PIL for further processing
        pil_image = Image.fromarray(cropped_image)

        # Enhance contrast
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(2)  # Increase contrast

        # Apply a filter to sharpen the image
        sharpened_image = enhanced_image.filter(ImageFilter.SHARPEN)

        processed_image_key = f"processed_{os.path.splitext(document_key)[0]}.png"
        processed_image_path = f"/tmp/{processed_image_key}"
        sharpened_image.save(processed_image_path)

        return processed_image_path, processed_image_key

    def extract_data(self, document_key):
        response = self.textract_client.analyze_document(
            Document={"S3Object": {"Bucket": self.bucket_name, "Name": document_key}},
            FeatureTypes=["FORMS"]
        )
        
        text_blocks = [block['Text'] for block in response['Blocks'] if block['BlockType'] == 'LINE']
        full_text = "\n".join(text_blocks)
        key_values = {}

        # Extract dates from the compiled text
        dates = self.find_dates(full_text)

        return {
            "text": full_text,
            "keyValues": key_values,
            "dates": dates
        }
    
    def find_dates(self, text):
        # Pattern to match most common date formats
        full_date_pattern  = r'\b(20\d{2})[-/ ]?(0[1-9]|1[0-2])[-/ ]?(0[1-9]|[12]\d|3[01])\b|\b(0[1-9]|[12]\d|3[01])[-/ ]?(0[1-9]|1[0-2])[-/ ]?(20\d{2})\b'
        partial_date_pattern = r'\b(\d{2})[-/ ]?(0[1-9]|1[0-2])[-/ ]?(0[1-9]|[12]\d|3[01])\b|\b(0[1-9]|[12]\d|3[01])[-/ ]?(0[1-9]|1[0-2])[-/ ]?(\d{2})\b'

        full_dates = re.findall(full_date_pattern, text)
        partial_dates = re.findall(partial_date_pattern, text)

        formatted_dates = []

        # Handle full dates
        for date in full_dates:
            if date[0]:  # Format is YYYY-MM-DD
                year, month, day = date[0], date[1], date[2]
            else:  # Format is DD-MM-YYYY
                day, month, year = date[3], date[4], date[5]
            formatted_dates.append(f"{year}-{month}-{day}")

        # Handle partial dates (assuming they are meant to be in the 21st century)
        for date in partial_dates:
            if date[0]:  # Format is YY-MM-DD
                year, month, day = f"20{date[0]}", date[1], date[2]
            else:  # Format is DD-MM-YY
                day, month, year = date[3], date[4], f"20{date[5]}"
            formatted_dates.append(f"{year}-{month}-{day}")

        # Ensure all dates are in ISO 8601 format
        formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") for date in formatted_dates]

        return formatted_dates

if __name__ == "__main__":
    import config
    service = DocumentProcessingService(
        config.AWS_ACCESS_KEY_ID,
        config.AWS_SECRET_ACCESS_KEY,
        config.REGION_NAME,
        config.BUCKET_NAME
    )
    # Test the service
    # document_key = "aW4WOVd_700b.jpg"
    document_key = "20201224_130406.jpg"
    fdas = service.process_image(document_key, document_key)
    print(fdas)