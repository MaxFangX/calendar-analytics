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

    def __init__(self, timenodes=None):
        """
        Initializes a TimeNodeChain, and, if supplied, inserts an iterable of timenodes.
        """
        self.head = None
        if timenodes:
            self.insert_all(timenodes)


    def get_head(self):
        return self.head

    def insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time.
        Wrapper function for TimeNode.insert, so that TimeNodeChain().insert(node) mutates the chain object
        """
        if self.head:
            current = self.head.insert(timenode)
            while current.prev:
                current = current.prev
            self.head = current

        else:
            self.head = timenode

    def insert_all(self, timenodes):
        """
        Inserts an iterable of TimeNodes (list, QuerySet)
        If the list is ordered by start time, this operation will take roughly O(n)
        """
        if len(timenodes) == 0:
            return

        # Add the first node to avoid erroring on None.insert
        if self.head:
            last = self.head
            last.insert(timenodes[0])
        else:
            self.head = timenodes[0]
            last = self.head

        for i in range(1, len(timenodes)):
            node = timenodes[i]
            last.insert(node)
            last = node

        while last.prev:
            last = last.prev
        self.head = last

    def get_inverse(self):
        """
        Returns a TimeNodeChain representing the gaps between TimeNodes
        """
        # TODO use this somewhere to encourage completeness
        if not self.head:
            return None

        inverse = []
        current = self.head
        while current.next:
            if current.end == current.next.start:
                continue

            inverse.append(TimeNode(current.end, current.next.start, "GAP: {}--{}".
                format(current.id, current.next.id)))
            current = current.next

        chain = TimeNodeChain()
        chain.insert_all(inverse)
        return chain


class TimeNode:
    """
    Class representing a block of time.
    """

    def __init__(self, start, end, id=None):
        self.id = id
        self.prev = None
        self.next = None
        self.start = start
        self.end = end

    def insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the current node.
        """
        # TODO make this return the inserted node

        # Basic sanity chex
        if not self.start or not self.end or self.start > self.end:
            raise Exception("Base node missing start or end time, or start time > end time")
        if not timenode.start or not timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")
        if timenode.prev:
            print "Warning! Timenode '{}' to be inserted has a prev".format(timenode.id)
        if timenode.next:
            print "Warning! Timenode '{}' to be inserted has a next".format(timenode.id)

        # Go right
        current = self
        while timenode.start < current.end and current.next:
            current = current.next

        if timenode.start < current.end:  # Overwrite the current node
            if current.prev:
                current.prev.next = timenode
                timenode.prev = current.prev
                return timenode
            else:
                return timenode
        # TODO
        
        if not current.next:  # Easiest case - the current node is the last node
            if timenode.start >= current.end:
                if timenode.prev:
                    print "Warning! Overwriting timenode.prev"
                current.next = timenode
                timenode.prev = current
                return timenode
            else:
                # Conflicts with the current node; replace the current
                current.prev.next = timenode
                timenode.prev = current.prev
                return timenode
        else:  # Harder case - the current node is not the last node
            if timenode.start >= current.end:
                if current.next.start >= timenode.end:
                    current.next.prev = timenode
                    timenode.next = current.next
                    current.next = timenode
                    timenode.prev = current
                    return timenode
                else:
                    # Conflicts with current.next
                    after = current.next
                    while after.start < timenode.end:
                        if not after.next:
                            current.next = timenode
                            timenode.prev = current
                            return timenode
                        after = after.next
                    

    def old_insert(self, timenode):
        """
        Inserts a single TimeNode in O(n) time and returns the current node.
        """
        # TODO make this return the inserted node

        # Basic sanity chex
        if not self.start or not self.end or self.start > self.end:
            raise Exception("Base node missing start or end time, or start time > end time")
        if not timenode.start or not timenode.end or timenode.start > timenode.end:
            raise Exception("Timenode missing start or end time, or start time > end time")
        if timenode.prev:
            print "Warning! Timenode '{}' to be inserted has a prev".format(timenode.id)
        if timenode.next:
            print "Warning! Timenode '{}' to be inserted has a next".format(timenode.id)

        if timenode.start >= self.end:
            if self.next:
                # Handle the case of a "sandwiched" node
                if self.next.start >= timenode.end:
                    self.next.prev = timenode
                    timenode.next = self.next
                    self.next = timenode
                    timenode.prev = self
                else:
                    self.next = self.next.insert(timenode)
                    self.next.prev = self
            else:
                if timenode.prev:
                    print "Warning! Overwriting timenode.prev"
                self.next = timenode
                timenode.prev = self
            return self
        elif timenode.end <= self.start:
            if self.prev:
                # Handle the case of a "sandwiched" node
                if self.prev.end <= timenode.start:
                    self.prev.next = timenode
                    timenode.prev = self.prev
                    self.prev = timenode
                    timenode.next = self
                else:
                    self.prev = self.prev.insert(timenode)
                    self.prev.next = self
            else:
                if timenode.next:
                    print "Warning! Overwriting timenode.next of timenode '{}'".format(timenode.id)
                self.prev = timenode
                timenode.next = self
            return self
        else:
            # Remove the current node
            if self.prev:
                self.prev.next = self.next
            if self.next:
                self.next.prev = self.prev

            # Recurse; call insert on an adjacent node or return self
            if self.next:
                self.next.insert(timenode)
            elif self.prev:
                self.prev.insert(timenode)
            
            return timenode
