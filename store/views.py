from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Avg
from .models import Product, Cart, CartItem, Order, OrderItem, Category, Review

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

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

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

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Create session if it doesn't exist
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

    if not created:
        item.quantity += 1
        item.save()

    return redirect('cart')


def cart(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(session_key=session_key).first()

    if cart:
        items = cart.items.all()

        for item in items:
            item.total_price = item.product.price * item.quantity
    else:
        items = []

    return render(request, 'store/cart.html', {'items': items})

def remove_from_cart(request, item_id):
    item = CartItem.objects.filter(id=item_id).first()

    if item:
        item.delete()

    return redirect('cart')
    
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('cart')

def place_order(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(session_key=session_key).first()

    if not cart or not cart.items.exists():
        return redirect('cart')

    total = 0

    for item in cart.items.all():
        total += item.product.price * item.quantity

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

    cart.items.all().delete()

    return redirect('order_history')
def order_history(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    orders = Order.objects.filter(
        session_key=session_key
    ).order_by('-created_at')

    return render(
        request,
        'store/order_history.html',
        {'orders': orders}
    )

from django.contrib.auth.models import User
from django.contrib.auth import login

def register(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            error = 'Username already exists. Please choose another one.'
        elif username and password:
            user = User.objects.create_user(
                username=username,
                password=password
            )

            login(request, user)

            return redirect('home')

    return render(
        request,
        'store/register.html',
        {'error': error}
    )

from django.contrib.auth import authenticate, login, logout

def user_login(request):
    error = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('home')
        else:
            error = 'Invalid username or password.'

    return render(
        request,
        'store/login.html',
        {'error': error}
    )

def user_logout(request):
    logout(request)
    return redirect('home')

def checkout(request):
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key

    cart = Cart.objects.filter(session_key=session_key).first()

    if not cart or not cart.items.exists():
        return redirect('cart')

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        total = 0

        for item in cart.items.all():
            total += item.product.price * item.quantity

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

        cart.items.all().delete()

        return redirect('order_history')

    return render(request, 'store/checkout.html')
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

    return redirect('product_detail', product_id=product.id)