from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_verification_email(user, token):
    """Send email verification link to user."""
    
    # Verification URL (adjust based on your frontend URL)
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token.token}"
    
    subject = 'Verify Your Email Address'
    
    # Plain text message
    message = f"""
    Hello {user.get_full_name()},
    
    Thank you for registering with our E-Commerce Platform!
    
    Please verify your email address by clicking the link below:
    {verification_url}
    
    This link will expire in 24 hours.
    
    If you didn't create an account, please ignore this email.
    
    Best regards,
    E-Commerce Team
    """
    
    # HTML message (optional, more professional)
    html_message = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4CAF50;">Welcome to E-Commerce Platform!</h2>
                <p>Hello {user.get_full_name()},</p>
                <p>Thank you for registering with us. Please verify your email address to activate your account.</p>
                <div style="margin: 30px 0;">
                    <a href="{verification_url}" 
                       style="background-color: #4CAF50; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email Address
                    </a>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This link will expire in 24 hours. If you didn't create an account, 
                    please ignore this email.
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    E-Commerce Platform<br>
                    This is an automated email, please do not reply.
                </p>
            </div>
        </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending verification email: {e}")
        return False


def send_vendor_approval_email(user, approved=True):
    """Send email notification about vendor request status."""
    
    if approved:
        subject = 'Congratulations! Your Vendor Request Has Been Approved'
        message = f"""
        Hello {user.get_full_name()},
        
        Great news! Your vendor account request has been approved.
        
        You can now start selling products on our platform. Login to your account 
        and navigate to the products section to add your first product.
        
        Thank you for joining our platform!
        
        Best regards,
        E-Commerce Team
        """
    else:
        subject = 'Update on Your Vendor Request'
        message = f"""
        Hello {user.get_full_name()},
        
        Thank you for your interest in becoming a vendor on our platform.
        
        After careful review, we are unable to approve your vendor request at this time.
        
        If you have any questions, please contact our support team.
        
        Best regards,
        E-Commerce Team
        """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending vendor approval email: {e}")
        return False