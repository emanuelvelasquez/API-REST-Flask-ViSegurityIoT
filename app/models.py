# app/models.py


from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from app import db


class Usuario( db.Model):
    """
    Create an Usuario table
    """

    # Ensures table will be named in plural and not in singular
    # as is the name of the model
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    username = db.Column(db.String(60), index=True, unique=True)
    id_telegram = db.Column(db.String(50),index=True)
    nombre = db.Column(db.String(60), index=True)
    apellido = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    is_admin = db.Column(db.Boolean, default=False)

   
    def __repr__(self):
        return '<Usuario: {}>'.format(self.username)


# Set up user_loader
# @login_manager.user_loader
# def load_user(user_id):
#     return Usuario.query.get(int(user_id))



class Role(db.Model):
    """
    Create a Role table
    """

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    usuarios = db.relationship('Usuario', backref='role',
                                lazy='dynamic')

    def __repr__(self):
        return '<Role: {}>'.format(self.name)

class MedioNotificacion(db.Model):

    __tablename__= "medionotificaciones"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    

    def __repr__(self):
         return '<MedioNotificacion: {}>'.format(self.name)

class UsuarioNotificacion(db.Model):
    
    __tablename__= "usuarionotificacion"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    medionotificacion_id = db.Column(db.Integer, db.ForeignKey('medionotificaciones.id'))
    notificado = db.Column(db.Boolean, default=False)
  
    def __repr__(self):
         return '<UsuarioNotificacion: {}>'.format(self.usuario_id)

class Funciones(db.Model):
    
    __tablename__= "funciones"

    id = db.Column(db.Integer, primary_key=True)
    funcion = db.Column(db.String(30))
    corriendo = db.Column(db.Boolean, default=False)
    inicio = db.Column(db.Integer)
    fin = db.Column(db.Integer)
  
    def __repr__(self):
         return '<Funciones: {}>'.format(self.funcion)

class Eventos(db.Model):
    
    __tablename__= "eventos"

    id = db.Column(db.Integer, primary_key=True)
    evento = db.Column(db.String(30))
    hora = db.Column(db.DateTime, default=datetime.datetime.now)
    path = db.Column(db.String(100))
    revisado = db.Column(db.Boolean, default=False)
 
  
    def __repr__(self):
         return '<Eventos: {}>'.format(self.evento)

class Configuraciones(db.Model):

    __tablename__= "configuraciones"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    config = db.Column(db.String(100))
    descripcion = db.Column(db.String(100))


    def __repr__(self):
         return '<Configuraciones: {}>'.format(self.config)