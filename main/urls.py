from django.urls import path
from . import views


urlpatterns = [
  path('',views.home,name='home'),
  path('supplierpage/',views.supplierPage,name ='supplier'),
  path('purchasepage/',views.purchasePage,name = 'purchase'),
  path('receive/<str:purchase_id>',views.receive,name = 'receive'),
  path('stock',views.stock,name = 'stock'),
  path('stock/<str:stockid>',views.stockOut,name='stockout'),
  path('stockinprompt/<str:stockid>',views.stockInPrompt,name='stockinprompt'),
  path('stockmovements/',views.stockMovements,name='stockmovements'),
]