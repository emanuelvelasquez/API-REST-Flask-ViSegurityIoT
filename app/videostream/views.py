from flask import render_template, abort, Response, Flask, redirect, url_for, flash, request,current_app, stream_with_context,jsonify
from flask_restful import Resource
from ..models import Funciones, Eventos, Configuraciones,Usuario, UsuarioNotificacion
from .. import db, mail , sched
from ..common.telegram_send import Send_Telegram, Send_Mensaje
from ..common.mail import envia_mail_eventos
import cv2, json
import time, datetime
from .imutil import CameraStream
import requests, os, json, base64
from requests.auth import HTTPBasicAuth
from .TFliteVideoStream import reconocimineto_stream

class VideoStreaming(Resource):
   
    #@videostream.route('/videostream/gen_frame/<string:url_cam>', methods=['GET'])
    def gen_frame(self,url_cam):
        
        cap = CameraStream(url_cam).start()
        """Video streaming generator function."""
        while cap:
            frame = cap.read()
            convert = cv2.imencode('.jpg', frame)[1].tobytes()
            
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + convert + b'\r\n') # concate frame one by one and show result

    #@videostream.route('/videostream/get_video/<string:id_cam>', methods=['GET'])
    def get(self,id_cam):
            
        print(id_cam)
        """Video streaming route. Put this in the src attribute of an img tag."""
        #reconocimineto_stream
        #gen_frame
        url_cam =Configuraciones.query.filter_by(descripcion=id_cam).first().config
        return Response(response=stream_with_context(self.gen_frame(url_cam)), mimetype='multipart/x-mixed-replace; boundary=frame')
      
            
    


class FuncionReconocimiento(Resource):

    #@videostream.route('/videostream/iniciar_fin',methods=['GET'])

    def post(self,correr=None,inicio_hs=0,fin_hs=0):
        funcion = Funciones.query.get_or_404(1)

        if correr:
            
        
            inicia= correr
            if inicia=='True':
                sched.remove_all_jobs()
                funcion.corriendo = 1
                #cargo array con los idTelegram de los usuarios configurados para Telegram
                Usuario_Telegram = UsuarioNotificacion.query.filter_by(medionotificacion_id=2)
                id_tele=[]
                for i in Usuario_Telegram:
                    usu = Usuario.query.get_or_404(i.usuario_id)
                    if usu.id_telegram is not None and usu.id_telegram != '':
                        i=id_tele.append(usu.id_telegram)

                camaras=Configuraciones.query.filter_by(nombre='cam')

                #creo la tarea de reconocimiento para cada camara
                for cam in camaras:
                    
                    sched.add_job(func=reconocimineto_stream, trigger='cron', args=[cam.config, funcion.fin, cam.descripcion,id_tele], minute=funcion.inicio, id=cam.descripcion)
                    
                #genero la tarea para que una vez finalise la tarea de reconocimiento se guarde los eventos en base de datos
                sched.add_job(func=self.novedades, trigger='cron', args=[funcion.fin, current_app._get_current_object()], minute = funcion.fin + 1 , id='eventos')


                #creo la tarea para guardar la novedades en la base de datos


                time.sleep(1)
                msg = 'Se inicio exitosamente la funcion de Reconocimiento!!!'

            else:
                funcion.corriendo = 0
                # jobss=sched.get_jobs().count()
                sched.remove_all_jobs()
                #sched.shutdown()
                msg = 'Se detuvo exitosamente la funcion de Reconocimiento!!!'
            
        else:
            funcion.inicio = inicio_hs
            funcion.fin = fin_hs
            msg = 'Se modifico el periodo exitosamente!!!'

        db.session.commit()

        return jsonify(msg=msg)


    def novedades(self,fin,app):

        with app.app_context():
            
            #sched.remove_all_jobs()

            #cargon en un listado las novedad de "text_eventos.txt"
            with open("/home/pi/Documents/API-REST-Flask-ViSegurityIoT/text_eventos.txt") as f: 
                lines = f.readlines()
                f.close()
            
            
            for e in lines:
                e1 = e.replace(',\n','')
                e2=e1.replace("'",'"')
                e3 = json.loads(e2)
            
                #cargo la lista de eventos a la base de datos
                evento=Eventos(evento=e3['evento'],hora=datetime.datetime.strptime(e3['hora'], '%d-%b-%Y-%H:%M:%S'),path=e3['path'],revisado=e3['revisado'])
                db.session.add(evento)
            
            db.session.commit()

            envia_mail_eventos(lines,app)
        

        #codigo para borrar el listado de eventos en la base de datos
        open('/home/pi/Documents/API-REST-Flask-ViSegurityIoT/text_eventos.txt', 'w').close()

        pass
        

    #@videostream.route('/videostream/jpg_get', methods=['POST'])
class Evento(Resource):

    def get(self,id_evento):
        # url=Configuraciones.query.filter_by(nombre='ngrok').first().config
        # response=requests.post(url + '/reconocimiento/False').text   
        # asdad= json.loads(response)['msg']
        evento = Eventos.query.get_or_404(id_evento)

        img = open(evento.path,"rb")
        base61jpg = base64.b64encode(img.read())

        return jsonify(img=base61jpg,dispositivo=evento.evento,hora=evento.hora)

