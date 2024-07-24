from django.contrib import admin
from cart.models import Cart,Order_table,Payment
from django.http import HttpResponse
admin.site.register(Cart)
admin.site.register(Order_table)
admin.site.register(Payment)
