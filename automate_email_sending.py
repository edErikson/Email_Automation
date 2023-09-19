''' You work at a company that sends daily reports to clients via email. The goal of this project is to automate the process of sending these reports via email.

    Here are the steps you can take to automate this process:

    Use the smtplib library to connect to the email server and send the emails.

    Use the email library to compose the email, including the recipient's email address, the subject, and the body of the email.

    Use the os library to access the report files that need to be sent.

    Use a for loop to iterate through the list of recipients and send the email and attachment.

    Use the schedule library to schedule the script to run daily at a specific time.

    You can also set up a log file to keep track of the emails that have been sent and any errors that may have occurred during the email sending process. '''

import smtplib
import ssl
import json
import os
import re
from getpass import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'config.json')
LOG_DIRECTORY = os.path.join(FILE_DIRECTORY, 'Logs')
os.makedirs(LOG_DIRECTORY, exist_ok=True)
ERROR_FILE = os.path.join(LOG_DIRECTORY, 'Error.log')

def get_recipients(filename):
    try:
        recipient_addresses = []
        warning_flag = True

        with open(filename, 'r') as recipients_file:
            for line in recipients_file:
                recipient = sanitize_email(line.strip())
                if recipient:
                    recipient_addresses.append(recipient)
                else:
                    log_file_path = os.path.join(LOG_DIRECTORY, 'invalid_recipient_addresses.log')

                    if warning_flag:
                        print(f'Warning: Invalid email address(s) found, check "{log_file_path}" for more info.')
                        warning_flag = False
                    
                    with open(log_file_path, 'a') as log_file:
                        log_file.write(f'Warning: Invalid email "{line.strip()}" in "{filename}."\n')

        if not recipient_addresses:
            raise Exception(f'No valid email address(s) found in "{filename}".')

        return recipient_addresses
    except FileNotFoundError:
        print(f'Error(s) occured, please check {ERROR_FILE} for more info')

        with open(ERROR_FILE, 'a') as log_file:
            log_file.write(f'Error: Recipients file "{filename}" not found.\n')

        return []
    except Exception as e:
        print(f'Error(s) occured, please check {ERROR_FILE} for more info')

        with open(ERROR_FILE, 'a') as log_file:
            log_file.write(f'Error: {e}\n')

        return []

def sanitize_email(email_address):
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,3}$'

    if re.match(email_pattern, email_address):
        return email_address

def send_email(email_address, email_password, recipient_addresses, subject, message, attachment_path = None):
    try:
        if not email_address and not email_password:
            raise Exception('Invalid email address and password.')

        gmail_address = sanitize_email(email_address)

        if not gmail_address:
            raise Exception(f'Invalid gmail address format "{email_address}", please correct the gmail address in "config.json".')

        gmail_password = email_password

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as gmail_server:
            gmail_server.login(gmail_address, gmail_password)

            for recipient in recipient_addresses:
                msg = compose_email(gmail_address, recipient, subject, message, attachment_path)
                # gmail_server.sendmail(gmail_address, recipient, msg.as_string())

                log_file_path = os.path.join(LOG_DIRECTORY, 'successful_sent_emails.log')
                with open(log_file_path, 'a') as log_file:
                    log_file.write(f'Success: Email sent to "{recipient.strip()}"\n')

        return True
    except Exception as e:
        print(f'Error(s) occured, please check {ERROR_FILE} for more info')

        log_file_path = os.path.join(LOG_DIRECTORY, 'failed_sent_emails.log')
        with open(log_file_path, 'a') as log_file:
            log_file.write(f'Error: {e}\n')

        print(f'Error: {e}')
        return False
        
def compose_email(email_address, recipient_address, subject, message, attachment_path = None):
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_address
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    if os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as attachment_file:
            part = MIMEApplication(attachment_file.read(), Name=os.path.basename(attachment_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)
    else:
        print(f'Error(s) occured, please check {ERROR_FILE} for more info')

        log_file_path = os.path.join(LOG_DIRECTORY, 'failed_email_attachments.log')
        with open(log_file_path, 'a') as log_file:
            log_file.write(f'Error: {attachment_file} not found.\n')

    return msg

def main(email_address, email_password, recipients_file, subject, message, attachment_path = None):
    recipient_email_addresses = get_recipients(recipients_file)

    if recipient_email_addresses:
        success = send_email(email_address, email_password, recipient_email_addresses, subject, message, attachment_path)

if __name__ == '__main__':
    with open(CONFIG_DIRECTORY, 'r') as f:
        config = json.load(f)

    email_address = config.get('email_address', '')
    email_password = config.get('email_password', '')
    recipients_file = config.get('recipients_file', '')
    subject = config.get('subject', '')
    message = config.get('message', '')
    attachment_path = config.get('attachment_path')  # This can be None
    main(email_address, email_password, recipients_file, subject, message, attachment_path)