import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Centralized email and notification dispatch service.
    Decoupled from specific email providers (SES, SendGrid, Postmark, Resend, or local SMTP).
    """

    @classmethod
    def send_purchase_confirmation(cls, order) -> bool:
        """
        Sends an order confirmation & digital curriculum access email to the purchaser.
        """
        try:
            subject = f"Your Access Confirmation: {order.primary_product_title} [Order #{order.order_number}]"
            recipient = order.customer_email
            
            context = {
                'order': order,
                'customer_name': order.customer_name or order.customer.name or "Valued Student",
                'site_name': settings.SITE_NAME,
                'site_url': settings.SITE_URL,
                'primary_product': order.primary_product,
                'order_items': order.items.all(),
            }

            html_content = render_to_string('emails/order_confirmation.html', context)
            text_content = render_to_string('emails/order_confirmation.txt', context)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            order.email_sent = True
            order.save(update_fields=['email_sent'])
            logger.info(f"Successfully sent purchase confirmation for Order #{order.order_number} to {recipient}")
            return True

        except Exception as e:
            logger.error(f"Failed to send purchase confirmation for Order #{order.order_number}: {e}")
            return False

    @classmethod
    def send_waitlist_confirmation(cls, lead) -> bool:
        """
        Sends welcome email when a user joins the future membership/Telegram waitlist.
        """
        try:
            subject = f"You're on the waitlist! - {settings.SITE_NAME}"
            recipient = lead.email

            context = {
                'lead': lead,
                'site_name': settings.SITE_NAME,
                'site_url': settings.SITE_URL,
            }

            html_content = render_to_string('emails/waitlist_confirmation.html', context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            logger.info(f"Sent waitlist confirmation to {recipient}")
            return True
        except Exception as e:
            logger.error(f"Failed to send waitlist confirmation to {lead.email}: {e}")
            return False

    @classmethod
    def send_contact_notification(cls, contact_message) -> bool:
        """
        Notifies creator about a new contact form submission.
        """
        try:
            subject = f"New Inquiry: {contact_message.name} - {contact_message.subject or 'General Question'}"
            context = {
                'message': contact_message,
                'site_name': settings.SITE_NAME,
                'site_url': settings.SITE_URL,
            }

            html_content = render_to_string('emails/contact_notification.html', context)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.NOTIFICATION_EMAIL],
                reply_to=[contact_message.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            logger.info(f"Sent contact notification for {contact_message.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send contact notification: {e}")
            return False

# Public helper functional API
send_purchase_confirmation = NotificationService.send_purchase_confirmation
send_waitlist_confirmation = NotificationService.send_waitlist_confirmation
send_contact_notification = NotificationService.send_contact_notification
