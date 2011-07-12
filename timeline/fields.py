from django.db import models
from django.core.exceptions import ValidationError

class ReleasedField(models.DateField):
    def clean_fields(self):
        try:
            super(ReleasedField, self)
        except ValidationError:
            if len(self.released) == 4 and int(self.released) >= 1900:
                self.released = self.released + '-01-01'
            else:
                self.released = '1970-01-01'
