import functools
import random


class ResultList(list):
    """
    Extends the list class with methods to retrieve the first or last value,
    or None if the list is empty, and additional methods for filtering,
    mapping, reducing, sorting, grouping, and selecting a random element.
    This class is used as a return value for returned documents
    """
    def __repr__(self) -> str:
        return "\n".join([repr(item) for item in self])

    def __str__(self) -> str:
        return "\n".join([str(item) for item in self])

    def first_or_none(self):
        """
        Return the first value or None if list is empty
        :return: First list element or None
        """
        return self[0] if len(self) > 0 else None
    
    def first(self):
        """
        Return the first value or None if list is empty
        Synonym for first_or_none
        :return: First list element or None
        """
        return self.first_or_none()

    def last_or_none(self):
        """
       Return the last value or None if list is empty
       :return: Last list element or None
       """
        return self[-1] if len(self) > 0 else None

    def last(self):
        """
        Return the last value or None if list is empty
        Synonym for last_or_none
        :return: Last list element or None
        """
        return self.last_or_none()
    
    
    def filter(self, predicate):
        """
        Return a new ResultList containing only elements that match a given predicate function
        :param predicate: A function that takes an element and returns a boolean value
        :return: A new ResultList containing only matching elements
        """
        return ResultList(filter(predicate, self))

    def map(self, mapper):
        """
        Apply a given function to each element in the list and return a new ResultList containing the results
        :param mapper: A function that takes an element and returns a new value
        :return: A new ResultList containing the results of applying the mapper function to each element
        """
        return ResultList(map(mapper, self))

    def reduce(self, reducer, initial=None):
        """
        Reduce the list to a single value using a given reducer function
        :param reducer: A function that takes two elements and returns a single value
        :param initial: An optional initial value to start the reduction
        :return: The final reduced value
        """
        if initial is not None:
            return functools.reduce(reducer, self, initial)
        else:
            return functools.reduce(reducer, self)

    def sort(self, key=None, reverse=False):
        """
        Sort the list in place using a given sorting function
        :param key: A function that takes an element and returns a value to sort by
        :param reverse: A boolean indicating whether to sort in descending order (default is ascending)
        :return: None
        """
        super().sort(key=key, reverse=reverse)

    def group_by(self, keyfunc):
        """
        Group the elements in the list by a given key function and return a dictionary where the keys are the group keys
        and the values are lists of elements in that group.
        :param keyfunc: A function that takes an element and returns a key to group by
        :return: A dictionary of group keys and lists of elements in each group
        """
        groups = {}
        for elem in self:
            key = keyfunc(elem)
            if key in groups:
                groups[key].append(elem)
            else:
                groups[key] = [elem]
        return groups

    def random(self):
        """
        Return a random element from the list
        :return: A random element from the list
        """
        return random.choice(self)