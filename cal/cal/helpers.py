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

    def insert(timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the head node. Use sparingly
        """

        if not self.start or self.end:
            raise Exception("Missing start or end time")
        if self.start > self.end:
            raise Exception("Start time must be after end time")

        if not self.tail and timenode.start >= self.end:
            self.tail = timenode
            return self
        elif self.tail and timenode.start >= self.end:
            self.tail.insert(timenode)
            return self
        elif timenode.end <= self.start:
            timenode.tail = self
            return timenode
        elif timenode.end > self.start and timenode.start <= self.start or
            timenode.start < self.end and timenode.end >= self.end or
            timenode.start <= self.start and timenode.end >= self.end or
            timenode.start >= self.start and timenode.end <= self.end:
            # TODO remove conflicting nodes
            raise Exception("Conflicting node")
