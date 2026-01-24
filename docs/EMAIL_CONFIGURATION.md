# Email Service Configuration Guide

## Overview
This guide provides configuration instructions for the email service in the user_management project.

## SMTP Configuration

### Configuration File
Update the following settings in `src/users/config/config.py` or set them as environment variables:

```python
# Email / SMTP Configuration
SMTP_HOST: str = "smtp.gmail.com"      # Your SMTP server
SMTP_PORT: int = 587                    # SMTP port (587 for TLS)
SMTP_USER: str = "your-email@gmail.com" # Sender email address
SMTP_PASSWORD: str = "your-app-password" # SMTP password or app password
```

### Environment Variables (.env)
Alternatively, create or update the `.env` file:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Provider-Specific Configuration

### Gmail

1. **Enable 2-Factor Authentication** on your Google account
2. **Generate an App Password**:
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification"
   - Scroll down to "App passwords"
   - Generate a new app password for "Mail"
   - Use this password in `SMTP_PASSWORD`

**Configuration**:
```python
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-16-char-app-password"
```

### Outlook/Office 365

**Configuration**:
```python
SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587
SMTP_USER = "your-email@outlook.com"
SMTP_PASSWORD = "your-password"
```

### SendGrid

**Configuration**:
```python
SMTP_HOST = "smtp.sendgrid.net"
SMTP_PORT = 587
SMTP_USER = "apikey"  # Literally the string "apikey"
SMTP_PASSWORD = "your-sendgrid-api-key"
```

### Amazon SES

**Configuration**:
```python
SMTP_HOST = "email-smtp.us-east-1.amazonaws.com"  # Your region
SMTP_PORT = 587
SMTP_USER = "your-smtp-username"
SMTP_PASSWORD = "your-smtp-password"
```

### Mailgun

**Configuration**:
```python
SMTP_HOST = "smtp.mailgun.org"
SMTP_PORT = 587
SMTP_USER = "postmaster@your-domain.mailgun.org"
SMTP_PASSWORD = "your-mailgun-password"
```

### Custom SMTP Server

**Configuration**:
```python
SMTP_HOST = "mail.yourdomain.com"
SMTP_PORT = 587  # or 465 for SSL, 25 for non-encrypted
SMTP_USER = "noreply@yourdomain.com"
SMTP_PASSWORD = "your-password"
```

## Testing Email Configuration

### Method 1: Python Script

Create a test script `test_email.py`:

```python
import asyncio
from users.services.email_service import send_otp_email, send_invite_email

async def test_emails():
    # Test OTP email
    print("Sending OTP email...")
    result1 = await send_otp_email("test@example.com", "123456")
    print(f"OTP email sent: {result1}")
    
    # Test invite email
    print("Sending invite email...")
    result2 = await send_invite_email(
        "test@example.com", 
        "https://yourapp.com/invite?token=abc123"
    )
    print(f"Invite email sent: {result2}")

if __name__ == "__main__":
    asyncio.run(test_emails())
```

Run the test:
```bash
cd /Users/admin/Documents/var/codebase/codehaus/user_management
python test_email.py
```

### Method 2: Using the API

1. Start the server:
```bash
cd /Users/admin/Documents/var/codebase/codehaus/user_management
./start.sh
```

2. Register a new user (this will trigger OTP email):
```bash
curl -X POST "http://localhost:5403/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "firstName": "Test",
    "lastName": "User",
    "tenantId": "LAWCO"
  }'
```

3. Check the logs for email sending status:
```bash
tail -f logs/app.log
```

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
**Error**: `SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')`

**Solutions**:
- Verify SMTP_USER and SMTP_PASSWORD are correct
- For Gmail, ensure you're using an App Password, not your regular password
- Check if 2FA is enabled (required for Gmail App Passwords)

#### 2. Connection Refused
**Error**: `ConnectionRefusedError: [Errno 61] Connection refused`

**Solutions**:
- Verify SMTP_HOST is correct
- Check if SMTP_PORT is correct (587 for TLS, 465 for SSL)
- Ensure your firewall allows outbound connections on the SMTP port

#### 3. TLS/SSL Issues
**Error**: `ssl.SSLError: [SSL: WRONG_VERSION_NUMBER]`

**Solutions**:
- Try using port 465 instead of 587
- Or modify the code to use `SMTP_SSL` instead of `SMTP` with `starttls()`

#### 4. Timeout
**Error**: `TimeoutError: [Errno 60] Operation timed out`

**Solutions**:
- Check your internet connection
- Verify the SMTP server is accessible
- Check if your ISP blocks SMTP ports

### Debug Mode

To enable detailed SMTP debugging, modify `email_service.py`:

```python
# Add this inside the send_email function, before connecting to SMTP
with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
    server.set_debuglevel(1)  # Enable debug output
    server.starttls()
    server.login(config.SMTP_USER, config.SMTP_PASSWORD)
    server.send_message(msg)
```

## Security Best Practices

1. **Never commit credentials**: Always use environment variables or secure vaults
2. **Use App Passwords**: For services like Gmail, use app-specific passwords
3. **Enable TLS**: Always use `starttls()` for secure connections
4. **Rotate passwords**: Regularly update SMTP credentials
5. **Monitor usage**: Track email sending to detect abuse
6. **Rate limiting**: Implement rate limiting to prevent spam

## Production Recommendations

### 1. Use a Dedicated Email Service
For production, consider using dedicated email services:
- **SendGrid**: Good free tier, excellent deliverability
- **Amazon SES**: Cost-effective, scalable
- **Mailgun**: Developer-friendly, good analytics
- **Postmark**: Focused on transactional emails

### 2. Implement Email Queue
For better reliability, implement an email queue using Redis:

```python
# Example: Queue email for later sending
await redis_client.lpush('email_queue', json.dumps({
    'to': to_email,
    'subject': subject,
    'html_body': html_body,
    'text_body': text_body
}))
```

### 3. Add Retry Logic
Implement exponential backoff for failed emails:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def send_email_with_retry(to_email, subject, html_body, text_body):
    return await send_email(to_email, subject, html_body, text_body)
```

### 4. Monitor Email Deliverability
- Track bounce rates
- Monitor spam complaints
- Verify sender domain (SPF, DKIM, DMARC)
- Use email validation before sending

## Email Templates Customization

To customize email templates, edit the HTML in `email_service.py`:

### OTP Email Template
Located in `send_otp_email()` function, starting at line ~60

### Invite Email Template
Located in `send_invite_email()` function, starting at line ~150

### Recommended Customizations
- Add your company logo
- Update color scheme to match your brand
- Add footer with company information
- Include social media links
- Add unsubscribe link (for marketing emails)

## Example: Custom Branding

```python
# Add to the HTML template
<div class="header" style="background-color: #YOUR_BRAND_COLOR;">
    <img src="https://yourcompany.com/logo.png" alt="Logo" style="height: 50px;">
    <h1>Account Verification</h1>
</div>
```

## Support

For issues or questions:
1. Check the logs in `logs/app.log`
2. Review SMTP provider documentation
3. Test with a simple SMTP client first
4. Contact your email service provider support
