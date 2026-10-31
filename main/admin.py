from django.contrib import admin
from .models import Suppliers,supplierItems,Purchase,PurchaseItem,Stock,StockIn,StockMovements,assets

# Register your models here.
admin.site.register(Suppliers)
admin.site.register(supplierItems)
admin.site.register(Purchase)
admin.site.register(PurchaseItem)
admin.site.register(Stock)
admin.site.register(StockIn)
admin.site.register(StockMovements)
admin.site.register(assets)