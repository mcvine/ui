# -*- Python -*-
#
# Jiao Lin <jiao.lin@gmail.com>
#


def notify(email, subject, context, template):
    '''send a notification email. a wrapper of "sendemail" function below.

    email: target email
    template: str template for email body
    context: a dict to format template
    '''
    body = template.format(**context)
    from .utils import sendmail
    try:
        sendmail(
            "mcvine.neutron@gmail.com", email,
            subject=subject, body=body
            )
    except Exception as e:
        import warnings
        warnings.warn(str(e))
        return
    return


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
