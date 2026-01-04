import re
from rest_framework.serializers import ValidationError

class LinkValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        reg = re.compile(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/')
        link = dict(value).get(self.field)
        if link and not re.match(reg, link):
            raise ValidationError("Разрешены только ссылки на YouTube")