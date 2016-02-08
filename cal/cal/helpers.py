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

    def insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the head node. Use sparingly
        """

        # Basic sanity chex
        if not self.start or self.end or self.start > self.end:
            raise Exception("Base node missing start or end time, or start time > end time")
        if not timenode.start or timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")
        if timenode.tail:
            print "Warning! Timenode to be inserted has a tail"

        if timenode.start >= self.end:
            if not self.tail:
                self.tail = timenode
            else:
                self.tail.insert(timenode)
                return self
            return self
        elif timenode.end <= self.start:
            if timenode.tail:
                print "Warning! Overwriting timenode.tail"
            timenode.tail = self
            return timenode
        else:
            # Overwrite the current node
            if not self.tail:
                return timenode
            else:
                # Recurse; call insert on the current tail
                return self.tail.insert(timenode)
            # TODO remove conflicting nodes
            raise Exception("Conflicting node")
