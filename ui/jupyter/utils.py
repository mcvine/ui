# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


def sendmail(me, to, subject, body):
    from email.mime.text import MIMEText
    # me == the sender's email address
    # you == the recipient's email address
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = me
    msg['To'] = to
    import smtplib
    s = smtplib.SMTP('localhost', port=25)
    s.sendmail(me, [to], msg.as_string())
    s.quit()
    return
    

# End of file 
