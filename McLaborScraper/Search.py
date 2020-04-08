class Search(object):
    """docstring for Search."""

    def __init__(self, entry, start, stop, isIndividual, numOfSearch = 0):
        super(Search, self).__init__()
        self.entry = entry
        self.start = start
        self.stop = stop
        self.isIndividual = isIndividual
        self.numOfSearch = numOfSearch
        self.worksheetSettings = None
