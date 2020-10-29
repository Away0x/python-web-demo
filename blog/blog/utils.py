from datetime import datetime

from django.core.cache import cache
from rest_framework_extensions.key_constructor.bits import KeyBitBase


class UpdatedAtKeyBit(KeyBitBase):
    key = "updated_at"

    def get_data(self, **kwargs):
        value = cache.get(self.key, None)
        if not value:
            value = datetime.utcnow()
            cache.set(self.key, value=value)
        return str(value)