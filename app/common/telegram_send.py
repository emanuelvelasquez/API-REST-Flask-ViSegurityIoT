import re,os,time
from flask import Flask, request
from flask import current_app as app
import telegram 
from .. import db
from ..models import Usuario ,Funciones, Eventos,UsuarioNotificacion
import sshtunnel
global bot
global TOKEN

TOKEN = '1470849315:AAHGZrvUGHI9seXxI9kqw4zPoz6_Dz5X_W4'
bot = telegram.Bot(token=TOKEN)

def Send_Telegram(imagen,objetos,cam,id_tele):
    
   
    for idtelegram in id_tele:
      
        print(cam)
        print(imagen)
        while not os.path.isfile(imagen):
            imagen=imagen
        # send the welcoming message
        texto_msg="Ntificacion de la camara '%a', se detecto: "% cam

        #sumo los objetos detectado
        for objeto in objetos:
            texto_msg= texto_msg + ' ' + objeto

        bot.send_message(chat_id=idtelegram,text=texto_msg)
        time.sleep(3)
        bot.send_photo(chat_id=idtelegram, photo=open(imagen,'rb'))
        

def Send_Mensaje(texto):
        
    chat_id= 1286962887
    bot.send_message(chat_id=chat_id,text=texto)

def carga_evento(id_cam,hora,path,revisado):
    
    #newapp = create_new_app()
    with app.app_context():
        
        eve= Eventos(evento=id_cam,hora=hora,path=path,revisado=revisado)
        db.session.add(eve)
        db.session.commit()
    
