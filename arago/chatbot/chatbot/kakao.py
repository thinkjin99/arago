import json
from django.views import View
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet


class ChatbotView(View):
    def post(self): ...

    def encode_to_json(self, query_set: QuerySet):
        data = json.dumps(list(query_set), cls=DjangoJSONEncoder)
        return data

    def create_response_message(self, outputs: list | dict):
        if not isinstance(outputs, list):
            outputs = [outputs]
        message = {
            "version": "2.0",
            "template": {"outputs": outputs},
        }
        return message
