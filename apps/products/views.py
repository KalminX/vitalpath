from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category

def course_list(request):
    """
    Catalog of published educational courses and digital guides.
    """
    category_slug = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()

    products = Product.objects.filter(status='published').select_related('category')
    categories = Category.objects.all()

    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    }
    return render(request, 'products/catalog.html', context)


def course_detail(request, slug):
    """
    Product detail page with full curriculum, FAQs, format details, and Stripe checkout CTA.
    """
    product = get_object_or_404(
        Product.objects.prefetch_related('modules', 'resources', 'faqs').select_related('category'),
        slug=slug,
        status='published'
    )

    related_products = Product.objects.filter(
        status='published'
    ).exclude(id=product.id)[:3]

    context = {
        'product': product,
        'modules': product.modules.all(),
        'resources': product.resources.all(),
        'faqs': product.faqs.all(),
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)
