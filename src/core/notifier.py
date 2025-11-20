"""
Notification module - handles sending notifications about new jobs.

Currently supports email via SMTP, but can be extended for Slack, Discord, etc.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from src.core import config


class EmailNotifier:
    """Email notification handler using Gmail SMTP."""
    
    def __init__(self):
        self.sender = config.EMAIL_SENDER
        self.password = config.EMAIL_PASSWORD
        self.recipient = config.EMAIL_RECIPIENT
    
    def format_job_email(self, jobs: List[Dict]) -> str:
        """
        Format jobs into a readable email body.
        
        Args:
            jobs: List of job dictionaries
            
        Returns:
            Formatted email body as string
        """
        if not jobs:
            return "No new jobs found."
        
        body = f"🎯 Found {len(jobs)} new software engineering internship posting(s)!\n\n"
        body += "=" * 70 + "\n\n"
        
        for i, job in enumerate(jobs, 1):
            body += f"{i}. {job['title']}\n"
            body += f"   Company: {job['company']}\n"
            body += f"   Location: {job['location']}\n"
            
            # Add salary if available
            if job.get('salary_min') and job.get('salary_max'):
                salary_min = f"${job['salary_min']:,.0f}"
                salary_max = f"${job['salary_max']:,.0f}"
                body += f"   Salary: {salary_min} - {salary_max}\n"
            
            body += f"   Apply: {job['url']}\n"
            body += f"   Posted: {job.get('posted_date', 'N/A')}\n"
            body += "\n" + "-" * 70 + "\n\n"
        
        body += "\nThis is an automated message from your LinkedIn Job Tracker.\n"
        body += "Apply early for the best chances! 🚀"
        
        return body
    
    def send_notification(self, jobs: List[Dict]) -> bool:
        """
        Send email notification for new jobs.
        
        Args:
            jobs: List of job dictionaries
        
        Returns:
            True if email sent successfully, False otherwise
        """
        if not jobs:
            print("  No new jobs to notify about")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['Subject'] = f"🚀 {len(jobs)} New SWE Intern Posting(s) Found!"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            # Format email body
            body = self.format_job_email(jobs)
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email via Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            print(f"✓ Email sent to {self.recipient}")
            print(f"  Notified about {len(jobs)} new job(s)")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send email: {e}")
            return False
    
    def send_test_email(self) -> bool:
        """
        Send a test email to verify configuration.
        
        Returns:
            True if test email sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart()
            msg['Subject'] = "✅ Job Tracker Setup Complete"
            msg['From'] = self.sender
            msg['To'] = self.recipient
            
            body = """
Hello!

This is a test email from your LinkedIn Job Tracker.

If you're receiving this, your email configuration is working correctly! ✓

The tracker will now send you notifications when new software engineering 
internship positions are found.

Configuration:
- Search: Software Engineer Intern positions
- Frequency: Based on your schedule settings
- Notification: Email (you're reading it!)

Next steps:
1. Let it run and collect data
2. Customize search parameters if needed
3. Check your email for new job notifications

Happy job hunting! 🚀

---
LinkedIn Job Tracker
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)
            
            print(f"✓ Test email sent successfully to {self.recipient}")
            return True
            
        except Exception as e:
            print(f"✗ Failed to send test email: {e}")
            print("  Check your email credentials and app password")
            return False


# Test function for standalone execution
if __name__ == "__main__":
    config.validate_config()
    
    notifier = EmailNotifier()
    
    # Send test email
    print("📧 Sending test email...")
    notifier.send_test_email()
