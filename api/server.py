import falcon
import os
from frictionless import Package, Resource
from wsgiref.simple_server import make_server

api = falcon.App()

print("Adding /app")
api.add_static_route('/app', os.path.abspath('../app'))

package = Package('../datapackage.json')

config_resources = os.getenv('RESOURCES', '').split(',')

def get_paginated_json(req, df):
    per_page = int(req.get_param('per_page', required=False, default=10))
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
                    print("Filtering on %s=%s" % (fn, q))
                    q = q.strip()
                    # q = int(q)
                    df = df.loc[df[fn] == q]
                except:
                    pass

        resp.status = falcon.HTTP_200
        resp.body = get_paginated_json(req, df)

for resource in package.resources:
    rn = resource['name']
    if not config_resources or rn in config_resources:
        print('Adding resource: /%s' % rn)
        api.add_route("/%s" % rn, DataResource(resource))

if __name__ == '__main__':
    with make_server('', 8000, api) as httpd:
        print('Serving on port 8000...')
        httpd.serve_forever()
