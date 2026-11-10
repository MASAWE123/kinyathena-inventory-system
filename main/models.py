from django.db import models

# Create your models here.
class Suppliers(models.Model):
  supplier=models.CharField(max_length=200)
  contact = models.CharField(max_length=200,null=True)
  phone = models.CharField(max_length=15,null=True)
  status =models.BooleanField(default=True ,null=True)

  def __str__(self):
    return self.supplier

class supplierItems(models.Model):
  supplier = models.ForeignKey(Suppliers,on_delete=models.CASCADE)
  itemName =models.CharField(max_length=200)
 
  def __str__(self):
     return self.itemName

class Purchase(models.Model):
  supplier = models.ForeignKey(Suppliers,on_delete=models.PROTECT)
  date_ordered = models.DateTimeField(auto_now_add=True)
  choices=[
    ("pending","Pending"),
    ("partial","Partially Received"),
    ("received","Received")
  ]
  status = models.CharField(max_length=20,choices=choices,default="pending")
  def __str__(self):
      return f'purchase {self.id}'
  
class PurchaseItem(models.Model):
   purchase = models.ForeignKey(Purchase,on_delete=models.CASCADE ,related_name='items')
   item = models.CharField(max_length=200)
   quantity_ordered = models.PositiveIntegerField(default=1)
   quantity_received = models.PositiveIntegerField(default=0)
   remaining = models.PositiveIntegerField()

   def __str__(self):
    return self.item

class Stock(models.Model):
  stock_status =[
    ('low_stock','LowStock'),
    ('outStock','Out_Of_Stock'),
    ('inStock','In_Stock')
  ]
  item = models.CharField(max_length=200,unique=True)
  quantity = models.PositiveIntegerField(default=0)
  status = models.CharField(choices=stock_status,null=True)
  low_stock_date = models.DateTimeField(null=True,blank=True)
  low_by = models.PositiveIntegerField(null=True,blank=True)

  def __str__(self):
    return self.item

class StockIn(models.Model):
    item = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()
    supplier = models.CharField(max_length=200,null=True,blank=True)
    date_received = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item

class StockOut(models.Model):
  item  = models.CharField(max_length=200,null=True)
  quantity = models.PositiveIntegerField(default=0)
  supplier_issued_to = models.CharField(max_length=200,null=True,blank=True)
  reason = models.CharField(max_length=200,null=True,blank=True)
  Notes = models.CharField(max_length=500,null=True,blank=True)

class StockMovements(models.Model):
  Movement_type=[
    ('in','Stock In'),
    ('Out','Stock Out'),
  ]
  item = models.CharField(max_length=200)
  quantity = models.PositiveIntegerField()
  supplier_issued_to = models.CharField(max_length=200,null=True,blank=True)
  date=models.DateTimeField(auto_now_add=True)
  movement = models.CharField(max_length=200,choices=Movement_type)
  reason = models.CharField(max_length=300,null=True,blank=True)
  note = models.CharField(max_length=1000,null=True,blank=True)

  def __str__(self):
    return f'{self.item}-{self.movement }'

class assets(models.Model):
  item = models.CharField(max_length=200)
  limit_quantity = models.PositiveIntegerField()

  def __str__(self):
    return f'{self.item} - {self.limit_quantity}'