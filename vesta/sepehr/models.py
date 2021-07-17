from django.db import models
import uuid
from datetime import datetime


def random_string():
    date = datetime.today().strftime('%Y_%m_%d_%H_%M_%S')
    random = uuid.uuid4().hex
    name_tab = random + "_" + date
    return name_tab


# address_rnd = models.CharField(max_length=250, blank=True, default='') #
# session_id = models.CharField(max_length=250, blank=True, default='') #
class Supplier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, blank=False)
    address = models.CharField(max_length=250, blank=False)
    username = models.CharField(max_length=250, blank=False)
    password = models.CharField(max_length=250, blank=False)
    status = models.BooleanField(default=False)
    credit = models.CharField(max_length=25, blank=False, default='0.0')
    name_rnd = models.CharField(max_length=250, blank=False, default=random_string)
    alias_name = models.CharField("alias name", max_length=250, blank=False, default='', help_text="نام مستعار")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.alias_name + ' - ' + self.address
