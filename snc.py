from sanic_dispatcher import SanicDispatcherMiddlewareController
from sanic import Sanic
from unscripted import wsgi

app = Sanic(__name__)

dispatcher = SanicDispatcherMiddlewareController(app)
# register the django wsgi application into the dispatcher
dispatcher.register_wsgi_application(wsgi.application,
                                             "/")

if __name__ == "__main__":
    app.run(port=8000, debug=True)

