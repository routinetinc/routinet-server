class Data():
    #def __init__(self, categoryid:int, score:int, priority:int, content_id:int):
    def __init__(self, category_id:int, score:int, content_id:int):
        self.category_id:int = category_id
        self.score:     int = score
        #self.priority:  int = priority
        self.content_id:int = content_id