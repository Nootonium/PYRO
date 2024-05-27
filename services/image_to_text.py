import boto3
import os
import dotenv

dotenv.load_dotenv()

aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
bucket_name = "noot-scan-storage"


def extract_data(document_key, bucket_name):
    # Initialize a Textract client
    textract = boto3.client(
        "textract",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name="us-east-1",
    )

    # Call Textract to process the document
    response = textract.analyze_document(
        Document={"S3Object": {"Bucket": bucket_name, "Name": document_key}},
        FeatureTypes=["FORMS", "QUERIES"],
        QueriesConfig={
        'Queries': [
            {
                'Text': 'DATE?',
                'Alias': 'date_query',
            },
        ]
    },
    )

    text_blocks = []
    key_values = {}
    dates = []

    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text_blocks.append(item["Text"])
        elif item["BlockType"] == "KEY_VALUE_SET":
            key_text = find_text(item, response["Blocks"], 'KEY')
            value_text = find_text(item, response["Blocks"], 'VALUE')
            key_values[key_text] = value_text
        elif item["BlockType"] == "QUERY_RESULT":
            # Ensure that the 'Query' key exists before accessing it
            if 'Query' in item and item["Query"]["Alias"] == "date_query":
                print(str(item))
                dates.append(item["Text"])

    # Construct the JSON object
    result = {
        "text": "\n".join(text_blocks),
        "keyValues": key_values,
        "dates": dates
    }
    return result

def find_text(item, blocks, block_type):
    text = ""
    for relationship in item.get('Relationships', []):
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                child_block = next((block for block in blocks if block['Id'] == child_id and block['BlockType'] == 'WORD'), None)
                if child_block:
                    text += child_block['Text'] + ' '
    return text.strip()


if __name__ == "__main__":
    document_key = '20201224_130406.jpg'
    # extracted_data = extract_data(document_key, bucket_name)
    # save_data_to_file(document_key, extracted_data)