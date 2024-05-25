from django.db import models

# Create your models here.

SHIPMENT_STATUS = {
    'PENDING': 0,
    'PROCESSING': 1,
    'PICKED_UP': 2,
    'IN_TRANSIT': 3,
    'DELIVERED': 4,
    'FAILED': 5
}


class Shipment(models.Model):
    first_name = models.CharField(max_length = 50)
    last_name = models.CharField(max_length = 50)
    address = models.CharField(max_length = 400, default = "")
    mobile = models.CharField(max_length = 10)
    order_id = models.PositiveBigIntegerField()
    status = models.PositiveIntegerField(default = SHIPMENT_STATUS['PENDING'])
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    deleted = models.PositiveBigIntegerField(default = 0)

    class Meta:
        db_table = 'shipments'
        verbose_name_plural = 'Shipments'

    ordering = ['-created_at']

    def __str__(self):
        return str(self.pk)
