class Search(object):
    """docstring for Search."""

    def __init__(self, entry, start, isIndividual, numOfSearch = 0):
        super(Search, self).__init__()
        self.entry = entry
        self.start = start
        self.stop = 150
        self.isIndividual = isIndividual
        self.numOfSearch = numOfSearch
        self.worksheetSettings = None
