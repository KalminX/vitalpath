from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .decorators import creator_required
from .forms import CreatorLoginForm, ProductForm, YouTubeVideoForm, CustomerNotesForm
from apps.products.models import Product, ProductModule, Category
from apps.orders.models import Order, Customer, Payment, WebhookEvent
from apps.content.models import YouTubeVideo
from apps.core.models import WaitlistLead, ContactMessage

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = CreatorLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                next_url = request.GET.get('next') or 'dashboard:overview'
                return redirect(next_url)
            else:
                messages.error(request, "This account does not have creator/staff management access.")
    else:
        form = CreatorLoginForm()

    return render(request, 'dashboard/login.html', {'form': form})


def dashboard_logout(request):
    logout(request)
    messages.info(request, "You have been logged out of the creator dashboard.")
    return redirect('core:home')


@creator_required
def dashboard_overview(request):
    """
    Main Creator KPI Overview with revenue, orders, customers, products,
    recent orders, top products, and recent activity.
    """
    paid_orders = Order.objects.filter(payment_status='paid')
    
    total_revenue = paid_orders.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_orders_count = paid_orders.count()
    total_customers_count = Customer.objects.count()
    total_products_count = Product.objects.filter(status='published').count()

    # Last 30 days revenue
    thirty_days_ago = timezone.now() - timedelta(days=30)
    month_revenue = paid_orders.filter(created_at__gte=thirty_days_ago).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    month_orders_count = paid_orders.filter(created_at__gte=thirty_days_ago).count()

    recent_orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')[:8]

    # Top selling products
    top_products = Product.objects.annotate(
        sales_count=Count('order_items', filter=Q(order_items__order__payment_status='paid')),
        revenue=Sum('order_items__price', filter=Q(order_items__order__payment_status='paid'))
    ).order_by('-sales_count', '-revenue')[:5]

    # Recent activity
    recent_leads = WaitlistLead.objects.order_by('-created_at')[:5]
    recent_messages = ContactMessage.objects.filter(is_read=False).order_by('-created_at')[:5]
    recent_webhooks = WebhookEvent.objects.order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders_count': total_orders_count,
        'total_customers_count': total_customers_count,
        'total_products_count': total_products_count,
        'month_revenue': month_revenue,
        'month_orders_count': month_orders_count,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_leads': recent_leads,
        'recent_messages': recent_messages,
        'recent_webhooks': recent_webhooks,
    }
    return render(request, 'dashboard/overview.html', context)


@creator_required
def product_list(request):
    """
    Creator product catalog management.
    """
    products = Product.objects.annotate(
        sales_count=Count('order_items', filter=Q(order_items__order__payment_status='paid'))
    ).order_by('-created_at')
    
    return render(request, 'dashboard/products_list.html', {'products': products})


@creator_required
def product_create(request):
    """
    Create a new course or guide.
    """
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Successfully created product: {product.title}")
            return redirect('dashboard:products_list')
    else:
        form = ProductForm()

    return render(request, 'dashboard/product_form.html', {'form': form, 'is_edit': False})


@creator_required
def product_edit(request, slug):
    """
    Edit existing product.
    """
    product = get_object_or_404(Product, slug=slug)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Changes saved for {product.title}")
            return redirect('dashboard:products_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'dashboard/product_form.html', {'form': form, 'product': product, 'is_edit': True})


@creator_required
def product_toggle_status(request, slug):
    """
    Quickly toggle between published and draft.
    """
    if request.method == 'POST':
        product = get_object_or_404(Product, slug=slug)
        if product.status == 'published':
            product.status = 'draft'
        else:
            product.status = 'published'
        product.save(update_fields=['status'])
        messages.success(request, f"Product status changed to {product.get_status_display()}")
    return redirect('dashboard:products_list')


@creator_required
def product_delete(request, slug):
    """
    Delete a product.
    """
    product = get_object_or_404(Product, slug=slug)
    if request.method == 'POST':
        title = product.title
        product.delete()
        messages.success(request, f"Product '{title}' was deleted.")
        return redirect('dashboard:products_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': product, 'type': 'Product'})


@creator_required
def order_list(request):
    """
    All orders with filtering and search.
    """
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()

    orders = Order.objects.select_related('customer').prefetch_related('items').order_by('-created_at')

    if status_filter:
        orders = orders.filter(payment_status=status_filter)

    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer_email__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(items__product_title__icontains=query)
        ).distinct()

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'dashboard/orders_list.html', context)


@creator_required
def order_detail(request, pk):
    """
    Detailed single order view with customer, line items, and Stripe payment metadata.
    """
    order = get_object_or_404(
        Order.objects.select_related('customer').prefetch_related('items', 'payments'),
        pk=pk
    )
    return render(request, 'dashboard/order_detail.html', {'order': order})


@creator_required
def customer_list(request):
    """
    Customer management and lifetime value tracking.
    """
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    customers = Customer.objects.all().order_by('-total_spent', '-created_at')

    if status_filter:
        customers = customers.filter(status=status_filter)

    if query:
        customers = customers.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query)
        )

    context = {
        'customers': customers,
        'query': query,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/customers_list.html', context)


@creator_required
def customer_detail(request, pk):
    """
    Single customer detail with notes and purchase history.
    """
    customer = get_object_or_404(Customer, pk=pk)
    orders = customer.orders.prefetch_related('items', 'payments').order_by('-created_at')

    if request.method == 'POST':
        form = CustomerNotesForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer notes updated.")
            return redirect('dashboard:customer_detail', pk=customer.pk)
    else:
        form = CustomerNotesForm(instance=customer)

    context = {
        'customer': customer,
        'orders': orders,
        'form': form,
    }
    return render(request, 'dashboard/customer_detail.html', context)


@creator_required
def video_list(request):
    """
    Manage educational YouTube video library.
    """
    videos = YouTubeVideo.objects.all().order_by('order', '-published_at')
    return render(request, 'dashboard/videos_list.html', {'videos': videos})


@creator_required
def video_create(request):
    """
    Add a new YouTube video lesson.
    """
    if request.method == 'POST':
        form = YouTubeVideoForm(request.POST)
        if form.is_valid():
            video = form.save()
            messages.success(request, f"Added video: {video.title}")
            return redirect('dashboard:video_list')
    else:
        form = YouTubeVideoForm()

    return render(request, 'dashboard/video_form.html', {'form': form, 'is_edit': False})


@creator_required
def video_edit(request, pk):
    """
    Edit existing YouTube video lesson.
    """
    video = get_object_or_404(YouTubeVideo, pk=pk)

    if request.method == 'POST':
        form = YouTubeVideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated video: {video.title}")
            return redirect('dashboard:video_list')
    else:
        form = YouTubeVideoForm(instance=video)

    return render(request, 'dashboard/video_form.html', {'form': form, 'video': video, 'is_edit': True})


@creator_required
def video_delete(request, pk):
    """
    Delete a YouTube video record.
    """
    video = get_object_or_404(YouTubeVideo, pk=pk)
    if request.method == 'POST':
        title = video.title
        video.delete()
        messages.success(request, f"Removed video: {title}")
        return redirect('dashboard:video_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': video, 'type': 'Video'})


@creator_required
def waitlist_list(request):
    """
    Review prospective members for Telegram & future memberships (Phases 2 & 3).
    """
    leads = WaitlistLead.objects.all().order_by('-created_at')
    return render(request, 'dashboard/waitlist_list.html', {'leads': leads})
