from flask_restful import Resource
from services import image_to_text, find_dates

class Textrack(Resource):
    def get(self, object_key):
        res = image_to_text.extract_data(object_key, "noot-scan-storage")
        res["dates"] = find_dates.find_dates(res["text"])
        return res