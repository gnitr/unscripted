import bjoern

from unscripted.wsgi import application

bjoern.run(application, '127.0.0.1', 8000)
