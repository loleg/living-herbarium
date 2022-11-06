import falcon
import json

from queryspecies import get_result, get_results


class SparqlResource:

    def on_get(self, req, resp):
        q = req.get_param('specie', None)
        mq = req.get_param('species', None)
        if q is not None:
            df = get_result(q)
        elif mq is not None:
            df = get_results(mq)
        else:
            df = {}
        resp.status = falcon.HTTP_200
        resp.text = json.dumps(df)
