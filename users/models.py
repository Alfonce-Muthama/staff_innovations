from django.db import models
from Base.models import BaseModel,GenericBaseModel



class User(BaseModel):
    username = models.CharField(max_length=100,null=True, blank=True)
    email= models.EmailField(max_length=100,null=True, blank=True)
    password = models.CharField(max_length=255,null=True, blank=True)
    first_name = models.CharField(max_length=150,null=True, blank=True)
    last_name = models.CharField(max_length=150,null=True, blank=True)
    role = models.ForeignKey('Role',on_delete=models.CASCADE,null=True, blank=True)
    department_id = models.ForeignKey('Department', on_delete=models.CASCADE, blank=False, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0,null=True, blank=True)



class Department(BaseModel):
    department_name = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)



class Role(GenericBaseModel):
    def __str__(self):
        return self.name













