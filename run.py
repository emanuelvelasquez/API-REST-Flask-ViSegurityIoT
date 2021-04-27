import os, random, string
from pyngrok import ngrok,conf,installer
from app import db
from app.models import Configuraciones


from app import create_app
config_name = os.getenv('FLASK_CONFIG')
app = create_app(config_name)#(config_name)development

alfabeto = string.ascii_lowercase

PassRamdom = ''.join(random.choice(alfabeto) for i in range(8))
#guardo el link de ngrok en la base de datos
#url = str(ngrok.connect(5000,auth="user-visegurityiot:"+ PassRamdom).public_url)

url = str(ngrok.connect(5000).public_url)
print(url)
with app.app_context():
   con = Configuraciones.query.filter_by(nombre='ngrok').first()
   con.config=url.replace('http://','https://')
   contra=Configuraciones.query.filter_by(nombre='pass-ngrok').first()
   contra.config=PassRamdom
   db.session.commit()


if __name__ == '__main__':
    app.run()




 
