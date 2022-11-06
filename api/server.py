import falcon
import os
from frictionless import Package
from wsgiref.simple_server import make_server
from datapackage import DataResource
from sparqlpackage import SparqlResource

api = falcon.App()

print("Adding /app")
api.add_static_route('/app', os.path.abspath('../app'))


package = Package('../datapackage.json')

config_resources = os.getenv('RESOURCES', None)
SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))

for resource in package.resources:
    rn = resource['name']
    if not config_resources or rn in config_resources:
        print('Adding resource: /%s' % rn)
        api.add_route("/%s" % rn, DataResource(resource))


api.add_route("/sparql", SparqlResource())
print('Adding /sparql endpoint')

if __name__ == '__main__':
    with make_server('', SERVER_PORT, api) as httpd:
        print('Serving on port %d...' % SERVER_PORT)
        httpd.serve_forever()
