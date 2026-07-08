from django.db import models
from django.utils import timezone

class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_deleted and not self.deleted_at:
            self.deleted_at = timezone.now()
        elif not self.is_deleted:
            self.deleted_at = None
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save()
        return 1, {self._meta.label: 1}
