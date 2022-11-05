import falcon
import os
import json
from frictionless import Package
from wsgiref.simple_server import make_server

from queryImage import get_results

api = falcon.App()

print("Adding /app")
api.add_static_route('/app', os.path.abspath('../app'))

package = Package('../datapackage.json')

config_resources = os.getenv('RESOURCES', None)
SERVER_PORT = int(os.getenv('SERVER_PORT', 8000))


def get_paginated_json(req, df):
    per_page = int(req.get_param('per_page', required=False, default=100))
    page = (int(req.get_param('page', required=False, default=1))-1)*per_page
    return df[page:page+per_page].to_json(orient='records')


class DataResource:

    def __init__(self, resource):
        self.resource = resource
        self.data = resource.to_pandas()

    def on_get(self, req, resp):
        df = self.data
        for fld in self.resource.schema.fields:
            fn = fld['name']
            q = req.get_param(fn, None)
            if q is not None:
                try:
                    q = q.strip()
                    # q = int(q)
                    df = df.loc[df[fn] == q]
                except:
                    print("Skipping filter on %s=%s" % (fn, q))

        resp.status = falcon.HTTP_200
        resp.text = get_paginated_json(req, df)


for resource in package.resources:
    rn = resource['name']
    if not config_resources or rn in config_resources:
        print('Adding resource: /%s' % rn)
        api.add_route("/%s" % rn, DataResource(resource))


class SparqlResource:

    def on_get(self, req, resp):
        q = req.get_param('species', None)
        if q is not None:
            df = get_results(q)
        else:
            df = {}
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(df)


api.add_route("/sparql", SparqlResource())

if __name__ == '__main__':
    with make_server('', SERVER_PORT, api) as httpd:
        print('Serving on port %d...' % SERVER_PORT)
        httpd.serve_forever()
