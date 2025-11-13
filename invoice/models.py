from django.db import models
from companies.models import Selfassesment, Limited
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver



class Company(models.Model):
    class Meta:
        verbose_name_plural = "Companies"
        constraints = [
                models.CheckConstraint(condition=models.Q(selfassesment__isnull=True) | models.Q(limited__isnull=True), name='limited_or_selfassesment_per_row'),
            ]

    selfassesment = models.ForeignKey(Selfassesment, on_delete=models.CASCADE, null=True, blank=True)
    limited = models.ForeignKey(Limited, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.company)

    @property
    def is_limited(self):
        return True if self.limited else False
    
    @property
    def is_selfassesment(self):
        return True if self.selfassesment else False
    

    @property
    def company(self):
        return self.selfassesment if self.selfassesment else self.limited

@receiver(post_save, sender=Selfassesment, dispatch_uid="add_selfassesment_to_company")
def add_selfassesment_to_company(sender, instance, created, **kwargs):
    if created:
        Company.objects.create(selfassesment=instance)

@receiver(post_save, sender=Limited, dispatch_uid="add_limited_to_company")
def add_limited_to_company(sender, instance, created, **kwargs):
    if created:
        Company.objects.create(limited=instance)



class Invoice(models.Model):
    invoice_to = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoice_to')
    customer_email = models.CharField(max_length=100, default='')
    billing_address = models.CharField(max_length=255, default='')
    remarks = models.TextField(default='')

    creation_timestamp = models.DateTimeField(auto_now_add=True)
    service_date = models.DateField()
    due_date = models.DateField()

    amount = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    is_paid = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"#{self.id} To: {self.invoice_to}"

# @receiver(pre_save, sender=Invoice, dispatch_uid="update_client_contact_info")
# def update_client_contact_info(sender, instance, **kwargs):
#     if instance.invoice_to.is_limited:
#         instance.customer_email = instance.invoice_to.limited.director_email
#         instance.billing_address = instance.invoice_to.limited.director_address
#     else:
#         instance.customer_email = instance.invoice_to.selfassesment.personal_email
#         instance.billing_address = instance.invoice_to.selfassesment.personal_address
    


class InvoiceItem(models.Model):
    name = models.CharField(max_length=255, default='')
    description = models.TextField()
    rate = models.FloatField()
    vat_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, default=None)

    def __str__(self) -> str:
        return f"Name: {self.name}, Rate: {self.rate}, Vat Percent: {self.vat_percent}"


class ItemsInInvoice(models.Model):
    class Meta:
        constraints = [
                models.UniqueConstraint(fields=['invoice_id', 'invoice_item_id'], name='unique_invoice_item')
            ]
        ordering = ['invoice_id', 'invoice_item_id']
    invoice_id = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    invoice_item_id = models.ForeignKey(InvoiceItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    rate = models.FloatField(default=0)
    vat_percent = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)], null=True, default=None)
    
    def __str__(self) -> str:
        return f"Id: {self.invoice_id}, Item Id: {self.invoice_item_id}"
    
    @property
    def amount(self):
        return self.rate * self.quantity
    
    @property
    def vat(self):
        if self.vat_percent is None:
            return 0
        return self.amount * self.vat_percent / 100
    
    @property
    def total(self):
        return self.amount + self.vat
    


class Transaction(models.Model):
    invoice_reference_id = models.ForeignKey(Invoice, on_delete=models.CASCADE, null=True)
    transaction_from = models.ForeignKey(Company, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_types = (
        ("CREDIT", "CREDIT"),
        ("DEBIT", "DEBIT"),
    )
    transaction_type = models.CharField(max_length=100, choices=transaction_types, default="CREDIT")
    current_balance = models.FloatField(default=0)
    amount = models.FloatField(default=0)

    def __str__(self) -> str:
        return f"#{self.id} To: {self.invoice_reference_id.invoice_to}"
