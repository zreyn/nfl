'''
This is the main Flask web app for the project.

We can test out the server by:
1) Creating a model: python src/build_model.py
2) Testing the model: python src/test_model.py
3) Running the server: python src/app.py
4) Open home page with the browser: http://localhost:8080/
'''


'''
==================================
IMPORTS
==================================
'''
import cPickle as pickle
from flask import Flask, render_template, request, jsonify
from build_model import DummyModel
import socket
import requests
import time
import datetime
import copy

'''
==================================
GLOBALS
==================================
'''
# register this as 'app'
app = Flask(__name__)

# load the current model
with open('data/model.pkl', 'r') as f:
    model = pickle.load(f)

'''
==================================
HELPER FUNCTIONS
==================================
'''



'''
==================================
Flask methods
==================================
'''
# dashboard/home page
@app.route('/')
def home_page():
    # pass the records to the template and render it
    return render_template('home.html')


'''
========================================================
If this is kicked from the command-line, run the server
========================================================
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
