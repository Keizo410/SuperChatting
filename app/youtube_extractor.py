# from aifc import Error
# import pytchat
# from googleapiclient.discovery import build


# livechat = pytchat.create(video_id="x9f_imB733s")
# while livechat.is_alive():
#     try:
#         for c in livechat.get().sync_items():
#             print(f"{c.datetime} [{c.author.name}] - {c.message}")
#             if c.amountValue:
#                 print(f"Superchat detected, {c.datetime} [{c.author.name}] - {c.amountValue}")
#     except KeyboardInterrupt:
#         livechat.terminate()
#         break


from flask import Flask
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route('/')
def main():
    return "Hello"

@app.route('/send')
def send_email():
    from_email = "keizo.kato410@gmail.com"  # Change to your email
    password = "jplm blkl gjoc nrbq"  # Change to your password
    to_email = "keizo.kato410@gmail.com"  # Change to recipient's email
    subject = "Test Subject"
    body = "This is a test message."

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the Gmail SMTP server
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(from_email, password)
        s.sendmail(from_email, to_email, msg.as_string())
        s.quit()
        return 'Mail has been sent successfully'
    except Exception as e:
        return f'Failed to send mail: {e}'

if __name__ == '__main__':
    app.run(port = 8000)