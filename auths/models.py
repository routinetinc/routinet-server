from django.db import models

class User(models.Model):
    table_name    = 'user'
    
    username         = models.CharField(max_length=20)   
    
    def __str__(self):
        return f"Task title is 「{self.username}」"