import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from accounts import constants
from threading import Thread


def send_email_with_thread(subject,message,to,email_lock):
    email_send_thread = Thread(target=send_email, args=(subject,
                                                              message,
                                                              to,
                                                              email_lock
                                                              ))
    email_send_thread.start()
def send_email(subject,message,to,email_lock):

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = constants.email
    msg['To'] = to

    # The main body is just another attachment
    body = MIMEText(message)
    msg.attach(body)
    print("message created")
    print(message)
    print("attachments attached")

    email_lock.acquire()
    try:
        s = smtplib.SMTP('smtp-mail.outlook.com', 587)
        print("connected to smtp")
        s.starttls()
        s.login(constants.email, constants.email_password)
        print("logged in to smtp")
        s.sendmail(constants.email, to, msg.as_string())
        print("e mail sent")
        s.quit()
        email_lock.release()
    except Exception as e:
        print(e)
        email_lock.release()
    print("connection exited")

def send_email_for_user_sign_up(ischair,to,email_lock):
    if ischair:
        message = "You applied to register as a chair. Admins will accept or reject your application. You are going to be notified by " \
                  "email soon."
        subject = "Your application to VICRM Conference as a chair."

    else:
        message = "You applied to register as a reviewer. Admins will accept or reject your application. You are going to be notified by " \
                  "email soon."
        subject = "Your application to VICRM Conference as a reviewer."
    send_email(subject, message, to,email_lock)