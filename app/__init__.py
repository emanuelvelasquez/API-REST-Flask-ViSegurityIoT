import os
import time
import sshtunnel
from flask import Flask, render_template
from flask_restful import Resource, Api, abort, reqparse
from flask_mail import Mail
#from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

#local import
from config import app_config

#inicializa db y login
db = SQLAlchemy()
#login_manager = LoginManager()
#migrate = Migrate(compare_type=True)
mail=Mail()
sched = BackgroundScheduler(daemon=True)
tunnel = sshtunnel.SSHTunnelForwarder(
    ('ssh.pythonanywhere.com'), ssh_username='upvisegurityiot', ssh_password='Sami2318',
    remote_bind_address=('upvisegurityiot.mysql.pythonanywhere-services.com', 3306),
    local_bind_address=('127.0.0.1', 10022)
    
)
 
tunnel.start()
print(tunnel.local_bind_port)


def create_app(config_name):
    if os.getenv('FLASK_CONFIG') == "production":
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=os.getenv('SQLALCHEMY_DATABASE_URI'),
            MAIL_SERVER = 'smtp.gmail.com',
            MAIL_PORT = 465,
            MAIL_USERNAME = 'visegurityiot@gmail.com',
            MAIL_PASSWORD = 'jfvdxflqqrxwpwbi',
            DONT_REPLY_FROM_EMAIL = '(Vi-Segurity-IoT, visegurityiot@gmail.com)',
            MAIL_USE_SSL= True,
            MAIL_USE_TLS = False

        )
    else:
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_object(app_config[config_name])
        app.config.update(
            SQLALCHEMY_DATABASE_URI = 'mysql://upvisegurityiot:Somali2318@127.0.0.1:10022/upvisegurityiot$visegurityiotdb2',
            SECRET_KEY='p9Bv<3Eid9%$i01',
            MAIL_SERVER = 'smtp.gmail.com',
            MAIL_PORT = 465,
            MAIL_USERNAME = 'visegurityiot@gmail.com',
            MAIL_PASSWORD = 'jfvdxflqqrxwpwbi',
            DONT_REPLY_FROM_EMAIL = '(Vi-Segurity-IoT, visegurityiot@gmail.com)',
            MAIL_USE_SSL= True,
            MAIL_USE_TLS = False

        )

    db.init_app(app)
   
    # login_manager.init_app(app)
    # login_manager.login_message = "Debes Iniciar Sesion!!!"
    # login_manager.login_view = "auth.login"    

    #migrate = Migrate(app, db)
    mail.init_app(app) 
    #Bootstrap(app)
    api = Api(app)

    sched.start()
    sched.remove_all_jobs()

    from app import models
    #import las clases
    from  .videostream import views as recurso 
    api.add_resource(recurso.VideoStreaming,'/videostream/<string:id_cam>')
    api.add_resource(recurso.FuncionReconocimiento,'/reconocimiento/<string:correr>')
    api.add_resource(recurso.FuncionReconocimiento,'/reconocimiento/<int:inicio_hs>/<int:fin_hs>',endpoint='reco')
    api.add_resource(recurso.Evento,'/evento/<int:id_evento>')

    return app
