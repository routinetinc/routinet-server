class Data():
    #def __init__(self, categoryid:int, score:int, priority:int, content_id:int):
    def __init__(self, categoryid:int, score:int, contentid:int):
        self.categoryid:int = categoryid
        self.score:     int = score
        #self.priority:  int = priority
        self.contentid:int = contentid