
from django.shortcuts import render,redirect
from .models import supplierItems,Suppliers,Purchase,PurchaseItem,Stock,StockIn,StockOut,StockMovements,assets
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import timedelta

# Create your views here.
def home(request):
  low_stock_table= Stock.objects.filter(status='low_stock').order_by('-id')
  stock_Movements = StockMovements.objects.all().order_by('-id')[:6]
  outStock = Stock.objects.filter(status='outStock').count()
  lowStock = Stock.objects.filter(status='low_stock').count()
  items = Stock.objects.all().count()
  suppliers_count= Suppliers.objects.all().count()
  print(items)
  context = {'suppliers_count':suppliers_count,'outStock':outStock,'lowStock':lowStock,'items':items,'stock_Movements':stock_Movements,'low_stock_table':low_stock_table}
  return render(request,'main/dashboard.html',context)

def supplierPage(request):
  suppliers = Suppliers.objects.all()[:10]
  suppliers_count= Suppliers.objects.count()
  suppliers_active = Suppliers.objects.filter(status=True).count()
  suppliers_inactive = Suppliers.objects.filter(status=False).count()
  context ={'suppliers':suppliers,'suppliers_count':suppliers_count,'suppliers_active':suppliers_active,'suppliers_inactive':suppliers_inactive}
  return render(request,'main/suppliers.html',context)

def purchasePage(request):
  if request.method == "POST":
    supplier_name = request.POST.get('supplier')
    supplier,created= Suppliers.objects.get_or_create(supplier=supplier_name)
    items = request.POST.getlist('item')
    quantities = request.POST.getlist('quantity')
     

    purchase =Purchase.objects.create(supplier=supplier)


    for item,quantity in zip(items,quantities):
      print(item,quantity)
      if not item or not quantity:
        continue

      existing_item =PurchaseItem.objects.filter(
        purchase =purchase,
        item = item.strip()
      ).first()
      if existing_item:
        existing_item.quantity_ordered += int(quantity)
        existing_item.save()
      else:
        purchaseitem = PurchaseItem.objects.create(
          purchase=purchase,
          item =item.strip(),
          quantity_ordered=int(quantity),
          remaining=int(quantity)
        )
  purchases = Purchase.objects.all().order_by('-id')
  purchase_count = Purchase.objects.count()
  purchase_pending_count = Purchase.objects.filter(status='pending').count()
  purchase_partial_count = Purchase.objects.filter(status='partial').count()
  purchase_received_count = Purchase.objects.filter(status='received').count()

  search_query = request.GET.get('q','').strip()
  if search_query:
    purchases = Purchase.objects.filter(
      Q(supplier__supplier__icontains=search_query)|Q(items__item__icontains=search_query)
    )

  selected_status = request.GET.get('status','').strip()
  if selected_status in dict(Purchase.choices):
    purchases = Purchase.objects.filter(status=selected_status)
 

  paginator = Paginator(purchases,7)  
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  context = {
    'purchases':purchases,
    'purchase_count':purchase_count,
    'page_obj':page_obj,
    'purchase_pending_count':purchase_pending_count,
    'purchase_partial_count':purchase_partial_count,
    'purchase_received_count':purchase_received_count,
    'selected_status':selected_status,
    }
  return render(request,'main/purchase.html',context)

def receive(request,purchase_id):
  purchase = Purchase.objects.get(id=purchase_id)
  purchaseItem = purchase.items.all()

  if request.method == "POST":
    for item in purchaseItem:
      quantity_received = request.POST.get(f'receive_{item.id}')

      if  not quantity_received:
        continue
      if int(quantity_received) > item.remaining:
        continue

      item.quantity_received += int(quantity_received)
      item.remaining = int(item.quantity_ordered-item.quantity_received)
      item.save()

      stock,created = Stock.objects.get_or_create(
        item=item.item.strip()
      )
      stock.quantity += int(quantity_received)
      stock.save()

      stockin = StockIn.objects.create(
        item=item.item.strip(),
        quantity = int(quantity_received)
      )
      StockMovements.objects.create(
              item=item.item,
              quantity = int(quantity_received),
              movement = 'in',
              reason='Nal'
    )

   

      

    if all(item.quantity_received == 0 for item in purchaseItem):
      purchase.status = 'pending'
    elif all(item.remaining == 0 for item in purchaseItem):
      purchase.status = 'received'

    else:
      purchase.status = 'partial'
    
    purchase.save()

      
    

  context = {
    'purchase':purchase,
    'purchaseItem':purchaseItem,
  }
  return render(request,'main/receive.html',context)

def stock(request):
  if request.method == 'POST':
    item_name = (request.POST.get('item_name') or '').strip()
    quantity = request.POST.get('quantity')
    supplier = (request.POST.get('supplier') or '').strip()

    if not item_name or not quantity:
      return redirect('stock')

    item_stock, created = Stock.objects.get_or_create(item=item_name)
    item_stock.quantity += int(quantity)
    stock_asset = assets.objects.filter(item=item_name).first()

    if item_stock.quantity == 0:
      item_stock.status = 'outStock'
    elif stock_asset and item_stock.quantity <= stock_asset.limit_quantity:
      item_stock.status = 'low_stock'
      item_stock.low_stock_date = timezone.now()
      item_stock.low_by = stock_asset.limit_quantity - item_stock.quantity
    else:
      item_stock.status = 'inStock'
    item_stock.save()

    StockIn.objects.create(
      item=item_name,
      quantity=int(quantity),
      supplier=supplier or None,
    )
  

  stock_query = Stock.objects.all().order_by('-id')

  search_query = request.GET.get('q', '').strip()
  if search_query:
    stock_query = stock_query.filter(
      Q(item__icontains=search_query) | Q(quantity__icontains=search_query)
      )
  selected_status = request.GET.get('status', '')
  if selected_status in dict(Stock.stock_status):
    stock_query = stock_query.filter(status=selected_status)

  stock_count = stock_query.count()
  low_stock_count = Stock.objects.filter(status='low_stock').count()
  in_stock_count = Stock.objects.filter(status='inStock').count()
  out_stock_count = Stock.objects.filter(status='outStock').count()
  stocks = stock_query.order_by('-id')
  asset_limits = assets.objects.all()

  paginator = Paginator(stock_query,7)  
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)
  context = {
    'stocks': stocks,
    'stock_count': stock_count,
    'asset': asset_limits,
    'search_query': search_query,
    'selected_status': selected_status,
    'low_stock_count': low_stock_count,
    'in_stock_count': in_stock_count,
    'out_stock_count': out_stock_count,
    'page_obj':page_obj,
  }
  return render(request,'main/inventory.html',context)

def stockOut(request,stockid):
  stock = Stock.objects.get(id=stockid)
  stockmovement = StockMovements.objects.all()
  stockOut = StockOut.objects.all()
  asset = assets.objects.filter(item=stock.item.strip()).first()


  if request.method == 'POST':
      quantity = request.POST.get('quantity')
      reason = request.POST.get('reason')
      notes = request.POST.get('notes')

      if int(quantity)== '':
        print('there is nothing')
        return redirect('stock')
      elif int(quantity) > stock.quantity:
        print('the value cannot be more than the quantity')
        return redirect('stock')
    

      stock.quantity -= int(quantity)
      stock.save()
      
      
      if stock.quantity == 0:
        stock.status = 'outStock'
      elif asset and stock.quantity <= asset.limit_quantity:
        stock.status = 'low_stock'
        stock.low_stock_date = timezone.now()
        lowby = asset.limit_quantity - stock.quantity
        stock.low_by = lowby
      else:
        stock.status = 'inStock'
      stock.save()



      StockMovements.objects.create(
          item=stock.item,
          quantity = int(quantity),
          supplier_issued_to = request.user.username,
          movement = 'Out',
          reason=str(reason),
          note =notes,
    )
      return redirect('stock')
  context = {
    'stock':stock,
  }

  return render(request,'main/stock_Out.html',context)

def stockInPrompt(request,stockid):
  stock = Stock.objects.get(id=stockid)
  stockmovement = StockMovements.objects.all()
  stockOut = StockOut.objects.all()
  asset = assets.objects.filter(item=stock.item.strip()).first()


  if request.method == 'POST':
      quantity = request.POST.get('quantity')
      reason = request.POST.get('reason')
      notes = request.POST.get('notes')

      if  not int(quantity):
        print('there is nothing')
        return redirect('stock')
      elif int(quantity) <= 0:
        print('the value cannot be less than or equal to zero')
        return redirect('stock')
    

      stock.quantity += int(quantity)
      stock.save()
     
      
      if stock.quantity == 0:
        stock.status = 'outStock'
      elif asset and stock.quantity <= asset.limit_quantity:
        stock.status = 'low_stock'
        stock.low_stock_date = timezone.now()
        lowby = asset.limit_quantity - stock.quantity
        stock.low_by = lowby
      else:
        stock.status = 'inStock'
      stock.save()



      StockMovements.objects.create(
          item=stock.item,
          quantity = int(quantity),
          supplier_issued_to = request.user.username,
          movement = 'In',
          reason=str(reason),
          note = notes,
    )
      return redirect('stock')
  context = {
    'stock':stock,
  }

  return render(request,'main/stockinprompt.html',context)

def stockMovements(request):
  stock_movements = StockMovements.objects.all().order_by('-id')
  today = timezone.localdate()
  start_of_week = today - timedelta(days=today.weekday())
  stock_movements_counts = stock_movements.count()
  today_count = stock_movements.filter(date__date=today).count()
  this_week_movements = stock_movements.filter(date__date__gte=start_of_week, date__date__lte=today).count()
  this_month_movements = stock_movements.filter(date__date__month=today.month, date__date__year=today.year).count()
  search_stock_movements = request.GET.get('q','').strip()
  if search_stock_movements:
    stock_movements= stock_movements.filter(
      Q(item__icontains=search_stock_movements)|
      Q(movement__icontains=search_stock_movements)
    )
  selected_status = request.GET.get('status','').strip()
  selected_movement_status = request.GET.get('movement_status','').strip()

  if selected_status == 'Today':
   stock_movements = stock_movements.filter(date__date=today)
  elif selected_status == 'This Week':
    stock_movements = stock_movements.filter(date__date__gte=start_of_week, date__date__lte=today)
  elif selected_status == 'This Month':
   stock_movements = stock_movements.filter(date__date__month=today.month, date__date__year=today.year)
  
  if selected_movement_status in dict(StockMovements.Movement_type):
   stock_movements = stock_movements.filter(movement=selected_movement_status)



  paginator = Paginator(stock_movements, 7) 
  page_number = request.GET.get('page')
  page_obj = paginator.get_page(page_number)

  context = {
    'stock_movements': stock_movements,
    'page_obj': page_obj,
    'today_count':today_count,
    'this_week_movements': this_week_movements,
    'this_month_movements': this_month_movements,
    'stock_movements_counts':stock_movements_counts,
    'selected_status':selected_status,
    'search_stock_movements':search_stock_movements,
    'selected_movement_status':selected_movement_status,
  }
  return render(request, 'main/stock_movements.html', context)

def stockMovements_details(request, movementid):
    stock=StockMovements.objects.get(id=movementid)
    context ={
      'stock':stock,
    }
    return render(request, 'main/stock_movement_details.html',context)