from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Vendor)
admin.site.register(CustomerProfile)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItems)


admin.site.index_title = "Bazar Sadai Admin"
admin.site.site_header = "Bazar Sadai Admin Panel"
admin.site.site_title = "Bazar Sadai Admin Panel"
