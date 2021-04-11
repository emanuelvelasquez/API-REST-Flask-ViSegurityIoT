from flask import Blueprint

videostream = Blueprint('videostream',__name__)

from . import views