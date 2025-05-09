from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from .forms import ProductForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.db.models import Count
from django.core.paginator import Paginator
from urllib.parse import unquote, quote
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Home view
def home(request):
    return render(request, 'home.html')

# Signup view
def signup(request):
    if request.method == 'POST':
        is_vendor = request.POST.get('is_vendor') == 'true'
        
        try:
            # Create User account
            user = User.objects.create_user(
                username=request.POST.get('username'),
                password=request.POST.get('password'),
                email=request.POST.get('email'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name')
            )
            
            if is_vendor:
                # Create Vendor profile
                Vendor.objects.create(
                    user=user,
                    store_name=request.POST.get('store_name'),
                    address=request.POST.get('address'),
                    phone_number=request.POST.get('phone_number'),
                    is_vendor=True
                )
                messages.success(request, 'Vendor account created successfully! Please wait for admin approval.')
            else:
                # Create Customer profile
                CustomerProfile.objects.create(
                    user=user,
                    address=request.POST.get('address'),
                    phone_number=request.POST.get('phone_number')
                )
                messages.success(request, 'Customer account created successfully!')
            
            # Log the user in
            login(request, user)
            
            # Redirect based on account type
            if is_vendor:
                return redirect('vendor_dashboard')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'signup.html')
    
    return render(request, 'signup.html')


# Login view
# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            if hasattr(user, 'vendor'):
                return redirect('vendor_dashboard')
            return redirect('home')
        else:
            messages.error(request, 'Invalid login credentials')
            return render(request, 'login.html')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.customer.phone_number = request.POST.get('phone_number')
        user.customer.address = request.POST.get('address')
        user.save()
        user.customer.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'profile.html', {'user': request.user})





# Get all products
def get_products(request):
    # Get the selected category from the query parameters, or default to 'All'
    selected_category = unquote(request.GET.get('category', 'All'))

    if selected_category == 'All':
        all_products = Product.objects.filter(is_active=True)
    else:
        all_products = Product.objects.filter(category=selected_category, is_active=True)

    # Pagination logic
    paginator = Paginator(all_products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'CATEGORY_CHOICES': Product.CATEGORY_CHOICES,
        'selected_category': selected_category,
    }
    return render(request, 'grocery.html', context)





@login_required
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    # Get all products for the vendor
    all_products = Product.objects.filter(vendor=request.user.vendor)
    total_products_count = all_products.count()  # Get the total count before pagination

    paginator = Paginator(all_products, 10)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    stats = {
        'total_products': total_products_count,  # Use the pre-pagination count
        'active_products': all_products.filter(is_active=True).count(),
        'low_stock': all_products.filter(stock__lt=10).count(),
    }

    context = {
        'products': products,
        'stats': stats,
        'CATEGORY_CHOICES': Product.CATEGORY_CHOICES,
    }
    return render(request, 'vendor_dashboard.html', context)

@login_required
def add_product(request):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            messages.success(request, 'Product added successfully.')
            return redirect('vendor_dashboard')
        else:
            messages.error(request, 'Invalid form submission.')
    else:
        form = ProductForm()
    
    
    category_choices = Product.CATEGORY_CHOICES
    
    return render(request, 'add_product.html', {
        'form': form,
        'category_choices': category_choices
    })

@login_required
def edit_product(request, product_id):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)

    if request.method == 'POST':
        try:
            # Update product fields
            product.name = request.POST.get('name')
            product.category = request.POST.get('category')
            product.description = request.POST.get('description')
            product.price = request.POST.get('price')
            product.stock = request.POST.get('stock')
            product.is_active = request.POST.get('is_active', '') == 'on'

            # Handle image update
            if 'image' in request.FILES:
                product.image = request.FILES['image']

            product.save()
            messages.success(request, 'Product updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')

        return redirect('vendor_dashboard')

    context = {
        'product': product,
        'CATEGORY_CHOICES': Product.CATEGORY_CHOICES,
    }
    return render(request, 'edit_product.html', context)

@login_required
def delete_product(request, product_id):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)

    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Product deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')

    return redirect('vendor_dashboard')

@login_required
def update_store(request):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    if request.method == 'POST':
        try:
            vendor = request.user.vendor
            vendor.store_name = request.POST.get('store_name')
            vendor.address = request.POST.get('address')
            vendor.phone_number = request.POST.get('phone_number')
            vendor.save()
            messages.success(request, 'Store information updated successfully!')
        except Exception as e:
            messages.error(request, f'Error updating store information: {str(e)}')

    return redirect('vendor_dashboard')

@login_required
def toggle_product_status(request, product_id):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id, vendor=request.user.vendor)
    
    try:
        product.is_active = not product.is_active
        product.save()
        status = 'activated' if product.is_active else 'deactivated'
        messages.success(request, f'Product {status} successfully!')
    except Exception as e:
        messages.error(request, f'Error toggling product status: {str(e)}')

    return redirect('vendor_dashboard')

@login_required
def vendor_logout(request):
    logout(request)
    return redirect('home')


# Cart and Order views
@login_required
def view_cart(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    cart_items = Cart.objects.filter(customer=request.user.customer)
    total_price = sum(item.total_price for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, product_id):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = Cart.objects.get_or_create(
        customer=request.user.customer,
        product=product,
        defaults={'quantity': quantity, 'total_price': product.price * quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.total_price = cart_item.quantity * product.price
        cart_item.save()

    messages.success(request, 'Product added to cart successfully!')
    return redirect('view_cart')

@login_required
def remove_from_cart(request, cart_id):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    cart_item = get_object_or_404(Cart, id=cart_id, customer=request.user.customer)
    cart_item.delete()
    messages.success(request, 'Product removed from cart successfully!')
    return redirect('view_cart')

@login_required
def clear_cart(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    Cart.objects.filter(customer=request.user.customer).delete()
    messages.success(request, 'Cart cleared successfully!')
    return redirect('view_cart')

@login_required
def increase_quantity(request, cart_id):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    cart_item = get_object_or_404(Cart, id=cart_id, customer=request.user.customer)
    cart_item.quantity += 1
    cart_item.total_price = cart_item.product.price * cart_item.quantity
    cart_item.save()

    messages.success(request, 'Quantity updated successfully!')
    return redirect('view_cart')

@login_required
def decrease_quantity(request, cart_id):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    cart_item = get_object_or_404(Cart, id=cart_id, customer=request.user.customer)
    cart_item.quantity -= 1
    cart_item.total_price = cart_item.product.price * cart_item.quantity
    cart_item.save()

    messages.success(request, 'Quantity updated successfully!')
    return redirect('view_cart')


@login_required
def checkout(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    cart_items = Cart.objects.filter(customer=request.user.customer)
    total_price = sum(item.total_price for item in cart_items)

    if request.method == 'POST':
        try:
            # Create the order for the customer
            order = Order.objects.create(
                customer=request.user.customer,
                total_price=total_price
            )
            # Add each cart item as an OrderItems entry
            for cart_item in cart_items:
                OrderItems.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    total_price=cart_item.total_price
                )
            # Clear the cart after order completion
            cart_items.delete()
            messages.success(request, 'Order placed successfully!')
            return redirect('checkout_success')
        except Exception as e:
            messages.error(request, f'Error placing order: {str(e)}')

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'checkout.html', context)


@login_required
def checkout_success(request):
    return render(request, 'checkout_success.html')

@login_required(login_url='login')
def view_orders(request):
    if not hasattr(request.user, 'customer'):
        messages.error(request, 'You do not have customer permissions.')
        return redirect('home')

    
    orders = Order.objects.filter(customer=request.user.customer).prefetch_related('items__product').order_by('-ordered_at')

    context = {
        'orders': orders,
    }
    return render(request, 'orders.html', context)


@login_required(login_url='login')
def Order_Management(request):
    if not hasattr(request.user, 'vendor'):
        messages.error(request, 'You do not have vendor permissions.')
        return redirect('home')

    vendor = request.user.vendor

    # Find orders that contain at least one product from this vendor
    orders = Order.objects.filter(items__product__vendor=vendor).distinct().prefetch_related('items__product', 'customer')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id)

        if not order.items.filter(product__vendor=vendor).exists():
            messages.error(request, "You don't have permission to update this order.")
            return redirect('vendor_dashboard')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected.")

        return redirect('vendor_dashboard')

    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'vendor_dashboard.html', context)
