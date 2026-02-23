"""
Email / SMTP configuration.
Update these settings with your email provider's details.

For Gmail:
  - SMTP_HOST = "smtp.gmail.com"
  - SMTP_PORT = 587
  - SMTP_USER = "your.email@gmail.com"
  - SMTP_PASSWORD = "your-app-password"   (use an App Password, not your regular password)

For Outlook/Hotmail:
  - SMTP_HOST = "smtp.office365.com"
  - SMTP_PORT = 587
"""

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""        # e.g. "school@gmail.com"
SMTP_PASSWORD = ""    # e.g. "abcd efgh ijkl mnop" (Gmail App Password)
SENDER_NAME = "School Management System"
