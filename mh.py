from meinheld import server
from unscripted.wsgi import application


def hello_world(environ, start_response):
    status = '200 OK'
    res = "Hello world!"
    response_headers = [
        ('Content-type', 'text/plain'),
        ('Content-Length', str(len(res)))]
    start_response(status, response_headers)
    return [res]


server.listen(("0.0.0.0", 8000))
server.set_keepalive(100)
server.run(application)
