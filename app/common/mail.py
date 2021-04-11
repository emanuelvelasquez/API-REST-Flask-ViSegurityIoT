import logging, re , os
from smtplib import SMTPException
from threading import Thread
from flask import current_app,render_template, Flask , request, current_app
from flask_mail import Message,Mail
from app import mail, db
import app as current
import json
from ..models import UsuarioNotificacion,Usuario
logger = logging.getLogger(__name__)

def _send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except SMTPException:
            logger.exception("Ocurrió un error al enviar el email")


def send_email(subject, sender, recipients, text_body,cc=None, bcc=None, html_body=None):
    msg = Message(subject, sender=sender, recipients=recipients, cc=cc, bcc=bcc)
    msg.body = text_body
    if html_body:
        msg.html = html_body
    

    Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()

def envia_mail_eventos(eventos,app):

    with app.app_context() as app:


        msg = Message(f'Notificacion de Alerta del Notificacion de alerta')
        msg.body = "Notificacion de alerta"
        msg.sender=  '(Vi-Segurity-IoT, visegurityiot@gmail.com)'
        msg.subject= 'Eventos'
        usus= UsuarioNotificacion.query.filter_by(medionotificacion_id=1)
        #cargo los mail de los usuarios que recibiran los mial co nla secuencia de eventos
        for usumedio in usus:
            msg.recipients.append(Usuario.query.filter_by(id=usumedio.usuario_id).first().email)

        idcrs=[]
        #armado de html
        for img in eventos:
            img1 = img.replace(',\n','')
            img2=img1.replace("'",'"')
            img3 = json.loads(img2)

            path= img3['path']
            nombre= path.split('/')
            nom= nombre[len(nombre)-1]
            idcrs.append({'nombre':nom,'camara':img3['evento'].upper(), 'hora':img3['hora']})
            msg.attach(nom,'image/jpg',open(img3['path'], 'rb').read(), 'inline', headers=[['Content-ID','<'+nom+'>']])
        
        html_body = render_template('template_mail/mail_novedades.html',idcrs=idcrs,)
        msg.html = html_body
        
        mail.send(msg)
        #Thread(target=_send_async_email, args=(current_app._get_current_object(), msg)).start()

    

        

