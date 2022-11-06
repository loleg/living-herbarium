import falcon
import json


class DataResource:

    def __init__(self, resource):
        self.resource = resource
        self.data = resource.to_pandas()

    def on_get(self, req, resp):
        df = self.data
        # Check for filter in query
        for fld in self.resource.schema.fields:
            fn = fld['name']
            q = req.get_param(fn, None)
            if q is not None:
                try:
                    q = q.strip()
                    # q = int(q)
                    df = df.loc[df[fn] == q]
                except:  # noqa
                    print("Skipping filter on %s=%s" % (fn, q))

        # Check for unique request
        unique = req.get_param("_unique", None)
        if unique:
            uniquelist = df[unique].unique().tolist()
            resp.text = json.dumps(uniquelist)

        else:
            # Return paginated data by default
            resp.text = get_paginated_json(req, df)

        # OK status
        resp.status = falcon.HTTP_200


def get_paginated_json(req, df):
    per_page = int(req.get_param('per_page', required=False, default=100))
    page = (int(req.get_param('page', required=False, default=1))-1)*per_page
    return df[page:page+per_page].to_json(orient='records')
