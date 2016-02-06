from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

import json


def json_response(data, status=200):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), status=status, content_type="application/json")


class TimeNode:

    def __init__(self, start, end, event_id=None):
        self.event_id = event_id
        self.tail = None
        self.start = start
        self.end = end
