#we go for production , we use this file for mail setup (Msg, subject, from , to , ect..)
"""import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_FROM

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(EMAIL_USER, EMAIL_PASSWORD)  # Login using App Password
            server.sendmail(EMAIL_FROM, to_email, msg.as_string())
            print(" Email sent successfully!")
    except Exception as e:
        print(f" Failed to send email: {e}")

"""