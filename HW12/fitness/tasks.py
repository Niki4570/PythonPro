import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery import Celery

app = Celery('fitness_app', broker='pyamqp://guest@localhost//', backend='rpc://')

@app.task
def send_mail(recipient, subject, text):
    print(f"Sending email to {recipient} with message {text}")
    print(f"Using password: {os.environ.get('EMAIL_PASSWORD')}")
    port = 587
    smtp_server = "smtp.gmail.com"
    sender_email = "nkrivoruchko125133@gmail.com"
    reciever_email = recipient
    password = os.environ.get('EMAIL_PASSWORD')
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient
    message['Subject'] = subject
    message.attach(MIMEText(text, 'plain'))

    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    with smtplib.SMTP(host=smtp_server, port=port) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, reciever_email, message.as_string())
