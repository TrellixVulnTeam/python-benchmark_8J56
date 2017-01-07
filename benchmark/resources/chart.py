import json

import bson.json_util
from flask import jsonify
from flask_restful import Resource

from benchmark.utils import log_util
from benchmark.utils import chart_util

LOG = log_util.get_logger(__name__)


class Chart(Resource):
    @staticmethod
    def get(chart_id):
        try:
            data = chart_util.construct_char(int(chart_id))
            data = json.loads(bson.json_util.dumps(data))
            ret = {"code": 0, "message": "", "data": data}
            return jsonify(ret)
        except Exception, exception:
            LOG.exception(exception)
            # traceback.format_exc()
            return jsonify({"code": 1, "message": str(exception)})
