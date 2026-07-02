from django.db import models
from Base.models import BaseModel,State



class User(BaseModel):
    username = models.CharField(max_length=100,null=True, blank=True)
    email= models.EmailField(max_length=100,null=True, blank=True)
    password = models.CharField(max_length=255,null=True, blank=True)
    first_name = models.CharField(max_length=150,null=True, blank=True)
    last_name = models.CharField(max_length=150,null=True, blank=True)
    role = models.CharField(max_length=100,null=True, blank=True)
    department_id = models.ForeignKey('Department', on_delete=models.CASCADE, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)



class Department(BaseModel):
    department_name = models.CharField(max_length=150,null=True, blank=True)
    description = models.TextField(null=True, blank=True)



class Role(BaseModel):
    description = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name







