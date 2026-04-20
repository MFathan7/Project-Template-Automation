import logging
import smtplib
import os
from email.message import EmailMessage
import mimetypes

logger = logging.getLogger(__name__)

def send_smtp_mail(
    server: str,
    port: int,
    username: str,
    password: str,
    to_email: str | list,
    subject: str,
    body: str,
    is_html: bool = False,
    cc_email: str | list = None,
    bcc_email: str | list = None,
    attachments: list = None
):
    """    
    :param server: Alamat server SMTP (contoh: smtp.office365.com atau smtp.gmail.com)
    :param port: Port SMTP (biasanya 587 untuk TLS)
    :param username: Email pengirim
    :param password: Password email pengirim (Gunakan App Password untuk Gmail/Outlook!)
    :param to_email: Email penerima (bisa string atau list of string)
    :param subject: Judul email
    :param body: Isi email
    :param is_html: True jika body berupa format HTML
    :param cc_email: Email CC (opsional)
    :param bcc_email: Email BCC (opsional)
    :param attachments: List of file paths untuk dilampirkan (opsional)
    """
    #logger.info(f"📧 SEND SMTP MAIL: Menyiapkan email untuk '{to_email}' dengan subject '{subject}'")
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = username
    
    msg['To'] = ", ".join(to_email) if isinstance(to_email, list) else to_email
    if cc_email:
        msg['Cc'] = ", ".join(cc_email) if isinstance(cc_email, list) else cc_email
    if bcc_email:
        msg['Bcc'] = ", ".join(bcc_email) if isinstance(bcc_email, list) else bcc_email

    # Set isi email
    if is_html:
        msg.set_content(body, subtype='html')
    else:
        msg.set_content(body)

    # Attachments
    if attachments:
        for filepath in attachments:
            if not os.path.exists(filepath):
                logger.warning(f"   ↳ ⚠️ Attachment gagal: File tidak ditemukan -> {filepath}")
                continue
                
            #logger.info(f"   ↳ Menempelkan attachment: {os.path.basename(filepath)}")
            
            ctype, encoding = mimetypes.guess_type(filepath)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'
            maintype, subtype = ctype.split('/', 1)
            
            with open(filepath, 'rb') as f:
                file_data = f.read()
                
            msg.add_attachment(
                file_data, 
                maintype=maintype, 
                subtype=subtype, 
                filename=os.path.basename(filepath)
            )

    #logger.info(f"   ↳ Mengkoneksikan ke server {server}:{port}...")
    try:
        if port == 465:
            smtp_server = smtplib.SMTP_SSL(server, port, timeout=30)
        else:
            smtp_server = smtplib.SMTP(server, port, timeout=30)
            smtp_server.starttls()
            
        smtp_server.login(username, password)
        smtp_server.send_message(msg)
        smtp_server.quit()
        
        #logger.info("   ↳ Pengiriman email berhasil ✅")
        
    except smtplib.SMTPAuthenticationError:
        logger.error("   ↳ ❌ Gagal Login: Username atau Password salah. (Jika pakai Gmail/Outlook 2FA, gunakan App Password!).")
        raise
    except Exception as e:
        logger.error(f"   ↳ ❌ Gagal mengirim email: {e}")
        raise