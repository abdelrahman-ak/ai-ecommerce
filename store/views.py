from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from .models import (
    Product,
    Cart,
    CartItem,
    Order,
    OrderItem,
    Category,
    Review,
)


# =========================
# HOME
# =========================

def home(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category_id=category)

    categories = Category.objects.all()

    return render(
        request,
        'store/home.html',
        {
            'products': products,
            'query': query,
            'categories': categories,
        }
    )


# =========================
# ADMIN DASHBOARD
# =========================

def admin_dashboard(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')

    products_count = Product.objects.count()

    orders_count = Order.objects.count()

    customers_count = User.objects.count()

    total_sales = sum(
        order.total_price
        for order in Order.objects.filter(
            status__in=[
                'Processing',
                'Shipped',
                'Delivered'
            ]
        )
    )

    low_stock_products = Product.objects.filter(
        stock__lte=3
    ).order_by('stock')

    recent_orders = Order.objects.all().order_by(
        '-created_at'
    )[:5]

    return render(
        request,
        'store/admin_dashboard.html',
        {
            'products_count': products_count,
            'orders_count': orders_count,
            'customers_count': customers_count,
            'total_sales': total_sales,
            'low_stock_products': low_stock_products,
            'recent_orders': recent_orders,
        }
    )

# =========================
# ADMIN - PRODUCTS
# =========================

def admin_products(request):
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all().order_by('name')

    return render(
        request,
        'store/admin_products.html',
        {
            'products': products,
            'categories': categories,
        }
    )


def admin_add_product(request):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')

    categories = Category.objects.all()

    if request.method == 'POST':

        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_id = request.POST.get('category')
        stock = request.POST.get('stock')
        image = request.FILES.get('image')

        if not name or not price or not category_id or not stock:

            messages.warning(
                request,
                'Please fill in all required fields.'
            )

            return render(
                request,
                'store/admin_product_form.html',
                {
                    'categories': categories,
                    'title': 'Add Product',
                }
            )

        category = get_object_or_404(
            Category,
            id=category_id
        )

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            category=category,
            stock=stock,
            image=image
        )

        messages.success(
            request,
            'Product added successfully.'
        )

        return redirect('admin_products')

    return render(
        request,
        'store/admin_product_form.html',
        {
            'categories': categories,
            'title': 'Add Product',
        }
    )


def admin_edit_product(request, product_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    categories = Category.objects.all()

    if request.method == 'POST':

        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')

        category_id = request.POST.get('category')

        if category_id:
            product.category = get_object_or_404(
                Category,
                id=category_id
            )

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        messages.success(
            request,
            'Product updated successfully.'
        )

        return redirect('admin_products')

    return render(
        request,
        'store/admin_product_form.html',
        {
            'product': product,
            'categories': categories,
            'title': 'Edit Product',
        }
    )


def admin_delete_product(request, product_id):

    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('home')

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if request.method == 'POST':

        product.delete()

        messages.success(
            request,
            'Product deleted successfully.'
        )

    return redirect('admin_products')
# =========================
# PRODUCT DETAILS
# =========================

def product_detail(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    recommended_products = Product.objects.filter(
        category=product.category
    ).exclude(
        id=product.id
    ).annotate(
        average_rating=Avg('reviews__rating')
    ).order_by(
        '-average_rating'
    )[:4]

    return render(
        request,
        'store/product_detail.html',
        {
            'product': product,
            'recommended_products': recommended_products,
        }
    )


# =========================
# CART
# =========================

def add_to_cart(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    # Check stock
    if product.stock <= 0:

        messages.warning(
            request,
            "Sorry, this product is currently out of stock."
        )

        return redirect('cart')

    # Create session
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart, created = Cart.objects.get_or_create(
        session_key=session_key
    )

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    # New item
    if created:

        item.quantity = 1
        item.save()

    # Existing item
    else:

        if item.quantity >= product.stock:

            messages.warning(
                request,
                f"Only {product.stock} units are available."
            )

        else:

            item.quantity += 1
            item.save()

    return redirect('cart')


def cart(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(
        session_key=session_key
    ).first()

    if cart:

        items = cart.items.all()

        for item in items:

            item.total_price = (
                item.product.price *
                item.quantity
            )

    else:

        items = []

    return render(
        request,
        'store/cart.html',
        {'items': items}
    )


def remove_from_cart(request, item_id):

    item = CartItem.objects.filter(
        id=item_id
    ).first()

    if item:
        item.delete()

    return redirect('cart')


def update_cart(request, item_id):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(
        session_key=session_key
    ).first()

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart
    )

    try:

        quantity = int(
            request.POST.get(
                'quantity',
                1
            )
        )

    except (TypeError, ValueError):

        messages.warning(
            request,
            "Please enter a valid quantity."
        )

        return redirect('cart')

    # Check stock
    if quantity > item.product.stock:

        messages.warning(
            request,
            f"Only {item.product.stock} units are available."
        )

        quantity = item.product.stock

    # Delete item
    if quantity <= 0:

        item.delete()

    else:

        item.quantity = quantity
        item.save()

    return redirect('cart')


# =========================
# ORDERS
# =========================

def place_order(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(
        session_key=session_key
    ).first()

    if not cart or not cart.items.exists():

        return redirect('cart')

    # Check stock
    for item in cart.items.all():

        if item.quantity > item.product.stock:

            messages.warning(
                request,
                f"Only {item.product.stock} units "
                f"of {item.product.name} are available."
            )

            return redirect('cart')

    total = 0

    for item in cart.items.all():

        total += (
            item.product.price *
            item.quantity
        )

    order = Order.objects.create(
        session_key=session_key,
        total_price=total
    )

    for item in cart.items.all():

        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

        # Reduce stock
        item.product.stock -= item.quantity
        item.product.save()

    cart.items.all().delete()

    return redirect('order_history')


def order_history(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    orders = Order.objects.filter(
        session_key=session_key
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'store/order_history.html',
        {'orders': orders}
    )


# =========================
# REGISTER
# =========================

def register(request):

    error = None

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        if User.objects.filter(
            username=username
        ).exists():

            error = (
                'Username already exists. '
                'Please choose another one.'
            )

        elif username and password:

            user = User.objects.create_user(
                username=username,
                password=password
            )

            login(
                request,
                user
            )

            return redirect('home')

    return render(
        request,
        'store/register.html',
        {'error': error}
    )


# =========================
# LOGIN
# =========================

def user_login(request):

    error = None

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(
                request,
                user
            )

            return redirect('home')

        else:

            error = (
                'Invalid username or password.'
            )

    return render(
        request,
        'store/login.html',
        {'error': error}
    )


# =========================
# LOGOUT
# =========================

def user_logout(request):

    logout(request)

    return redirect('home')


# =========================
# CHECKOUT
# =========================

def checkout(request):

    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(
        session_key=session_key
    ).first()

    if not cart or not cart.items.exists():

        return redirect('cart')

    # Check stock
    for item in cart.items.all():

        if item.quantity > item.product.stock:

            messages.warning(
                request,
                f"Only {item.product.stock} units "
                f"of {item.product.name} are available."
            )

            return redirect('cart')

    if request.method == 'POST':

        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Validate checkout data
        if not name or not address or not phone:

            messages.warning(
                request,
                "Please fill in all required fields."
            )

            return render(
                request,
                'store/checkout.html'
            )

        total = 0

        for item in cart.items.all():

            total += (
                item.product.price *
                item.quantity
            )

        order = Order.objects.create(
            session_key=session_key,
            name=name,
            address=address,
            phone=phone,
            total_price=total
        )

        for item in cart.items.all():

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Reduce stock
            item.product.stock -= item.quantity
            item.product.save()

        cart.items.all().delete()

        messages.success(
            request,
            "Your order has been placed successfully."
        )

        return redirect(
            'order_history'
        )

    return render(
        request,
        'store/checkout.html'
    )


# =========================
# REVIEWS
# =========================

def add_review(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    if not request.user.is_authenticated:

        return redirect('login')

    if request.method == 'POST':

        rating = request.POST.get(
            'rating'
        )

        comment = request.POST.get(
            'comment'
        )

        # Validate rating
        try:

            rating = int(rating)

        except (TypeError, ValueError):

            messages.warning(
                request,
                "Please enter a valid rating."
            )

            return redirect(
                'product_detail',
                product_id=product.id
            )

        if rating < 1 or rating > 5:

            messages.warning(
                request,
                "Rating must be between 1 and 5."
            )

            return redirect(
                'product_detail',
                product_id=product.id
            )

        # Prevent duplicate reviews
        if Review.objects.filter(
            product=product,
            user=request.user
        ).exists():

            messages.warning(
                request,
                "You have already reviewed this product."
            )

            return redirect(
                'product_detail',
                product_id=product.id
            )

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

    return redirect(
        'product_detail',
        product_id=product.id
    )