import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
from apps.products.models import Product
from .models import Order, Customer, Payment
from .services import StripeCheckoutService

logger = logging.getLogger(__name__)

def checkout_initiate(request, slug):
    """
    Initiates Stripe Checkout session for a product.
    """
    product = get_object_or_404(Product, slug=slug, status='published')
    customer_email = request.POST.get('email') or request.GET.get('email', '')

    session_result = StripeCheckoutService.create_checkout_session(
        product=product,
        customer_email=customer_email if customer_email else None,
        request=request
    )

    checkout_url = session_result.get('url')
    if not checkout_url:
        messages.error(request, "Unable to initiate payment session. Please try again or contact support.")
        return redirect('products:detail', slug=slug)

    return redirect(checkout_url)


def checkout_sandbox_simulator(request):
    """
    Interactive Stripe test mode payment simulator for client demonstration and portfolio review.
    Simulates the exact hosted Stripe checkout experience.
    """
    session_id = request.GET.get('session_id', 'cs_test_demo')
    product_slug = request.GET.get('product_slug', '')
    product = Product.objects.filter(slug=product_slug).first() or Product.objects.first()
    email = request.GET.get('email', '')

    context = {
        'session_id': session_id,
        'product': product,
        'email': email,
    }
    return render(request, 'orders/stripe_simulator.html', context)


@require_POST
def checkout_sandbox_complete(request):
    """
    Processes simulated test checkout completion, dispatching the exact same webhook
    and fulfillment lifecycle as Stripe live/test webhooks.
    """
    session_id = request.POST.get('session_id')
    product_slug = request.POST.get('product_slug')
    customer_email = request.POST.get('email', 'student@example.com').strip()
    customer_name = request.POST.get('name', '').strip() or customer_email.split('@')[0].capitalize()

    product = Product.objects.filter(slug=product_slug).first() or Product.objects.first()

    # Build simulated Stripe webhook payload
    session_data = {
        'id': session_id,
        'object': 'checkout.session',
        'customer_email': customer_email,
        'customer_details': {
            'email': customer_email,
            'name': customer_name,
        },
        'amount_total': int(product.price * 100) if product else 1900,
        'currency': 'usd',
        'payment_intent': f"pi_{session_id[-12:]}",
        'customer': f"cus_demo_{customer_email.split('@')[0]}",
        'metadata': {
            'product_id': str(product.id) if product else "1",
            'product_slug': product.slug if product else "fundamentals",
            'product_title': product.title if product else "Health Education Fundamentals",
        }
    }

    # Fulfill order idempotently
    order = StripeCheckoutService.process_checkout_completed(session_data)

    return redirect(f"/checkout/success/?session_id={session_id}")


def checkout_success(request):
    """
    Post-purchase success confirmation page.
    """
    session_id = request.GET.get('session_id')
    order = None

    if session_id:
        order = Order.objects.filter(stripe_checkout_session_id=session_id).first()

    if not order:
        # Check latest completed order if in session
        order = Order.objects.filter(status='completed').order_by('-created_at').first()

    context = {
        'order': order,
        'session_id': session_id,
    }
    return render(request, 'orders/success.html', context)


def checkout_cancel(request):
    """
    Payment cancellation or abandonment landing page.
    """
    product_slug = request.GET.get('product_slug', '')
    product = None
    if product_slug:
        product = Product.objects.filter(slug=product_slug).first()

    context = {
        'product': product,
    }
    return render(request, 'orders/cancel.html', context)


@csrf_exempt
def stripe_webhook(request):
    """
    Stripe Webhook HTTP Endpoint.
    Verifies HMAC signature and processes checkout events.
    """
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    success, message = StripeCheckoutService.verify_and_process_webhook(payload, sig_header)

    if success:
        return JsonResponse({'status': 'success', 'message': message}, status=200)
    else:
        return JsonResponse({'status': 'error', 'message': message}, status=400)
