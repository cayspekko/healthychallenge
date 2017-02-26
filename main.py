# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
from flask import Flask, request


app = Flask(__name__)


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    logging.critical("Does this message work or what?")
    return 'IT WOIKS!'

groupme_data = []
@app.route('/groupme', methods=['post', 'get'])
def groupme():
    if request.method == 'POST':
        json = request.get_json()
        logging.critical(request.get_json())
        groupme_data.append(json)
    return "<br><br>".join(str(d) for d in groupme_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
# [END app]
