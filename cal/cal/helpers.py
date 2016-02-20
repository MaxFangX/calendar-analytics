from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse

import json


def json_response(data, status=200):
    return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), status=status, content_type="application/json")


class TimeNodeChain:

    """
    A data structure that functions as a wrapper around a linked list of TimeNodes.
    It represents how someone is spending their time at different events. And since
    no one can be at two events at the same time, TimeNodes will overwrite any
    conflicting TimeNodes on insert.
    """

    def __init__(self, timenodes=None, is_sorted=False):
        """
        Initializes a TimeNodeChain, and, if supplied, inserts a list or QuerySet of 
        timenodes in an efficient manner.

        ~O(n) if sorted by start time, else O(nlog(n))
        """
        self.head = None
        if timenodes:
            self.insert_all(timenodes, is_sorted)


    def get_head(self):
        return self.head

    # TODO determine if this function is actually needed
    def insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time.
        Wrapper function for TimeNode.insert, so that TimeNodeChain().insert(node) mutates the chain object
        """
        if self.head:
            self.head = self.head.insert(timenode)
        else:
            self.head = timenode

    def insert_all(self, timenodes, is_sorted=False):
        """
        Inserts a list or QuerySet of timenodes in an efficient manner
        ~O(n) if sorted by start time, else O(nlog(n))
        """
        if not is_sorted:
            timenodes.sorted(key=lambda node: node.start)
        
        last = timenodes[0]
        self.head = last

        for i in range(1, len(timenodes)):
            node = timenodes[i]
            last.insert(node)
            last = node


class TimeNode:
    # TODO make this two way

    def __init__(self, start, end, id=None):
        self.id = id
        self.next = None
        self.start = start
        self.end = end

    def insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the head node.
        """

        # Basic sanity chex
        if not self.start or not self.end or self.start > self.end:
            raise Exception("Base node missing start or end time, or start time > end time")
        if not timenode.start or not timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")
        if timenode.next:
            print "Warning! Timenode to be inserted has a next"

        if timenode.start >= self.end:
            if not self.next:
                self.next = timenode
            else:
                self.next = self.next.insert(timenode)
                return self
            return self
        elif timenode.end <= self.start:
            if timenode.next:
                print "Warning! Overwriting timenode.next"
            timenode.next = self
            return timenode
        else:
            # Overwrite the current node
            if not self.next:
                return timenode
            else:
                # Recurse; call insert on the current next
                return self.next.insert(timenode)
