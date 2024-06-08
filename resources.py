from flask_restful import Resource
import config
from services import DocumentProcessingService

class DocumentProcessorResource(Resource):
    def __init__(self):
        self.document_processing_service = DocumentProcessingService(
            config.AWS_ACCESS_KEY_ID,
            config.AWS_SECRET_ACCESS_KEY,
            config.REGION_NAME,
            config.BUCKET_NAME
        )

    def get(self, object_key):
        image_path = self.document_processing_service.download_image_from_s3(object_key)
        processed_image_path, processed_image_key = self.document_processing_service.process_image(image_path, object_key)
        self.document_processing_service.upload_image_to_s3(processed_image_path, processed_image_key)
        res = self.document_processing_service.extract_data(processed_image_key)
        return res
