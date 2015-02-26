from flask import Flask, render_template, request, jsonify, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn 
import operator
import os
import requests
import re
import json
import time
import nltk
import subprocess
import random
import string

#################
# configuration #
#################

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
q = Queue(connection=conn)

from models import Result

#helper

def transcode_and_save_mesurments(data):

    errors = []
    
    input_url = "/home/tdeneke/easytrans/easytrans/videos/"+ data["url"]
    vid = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(11)])
    output_url = "/home/tdeneke/easytrans/easytrans/videos/" + vid
    container = "mp4" 

    cmd = "ffmpeg  -i " + input_url  + " -c:v " + data["codec"] + " -preset " + data["preset"] + " -s " + data["resolution"] + " -r " + data["framerate"] + " -b:v " + data["bitrate"] + " -y -f " + container +" "+ output_url

   
    try:
      #r = requests.get(url)
      print cmd
    except:
        errors.append(
            "Unable to get cmd. Please make sure it's valid and try again."
        )
        return {"error": errors}

    #transcode and mesure
    start = os.times()
    ls_output = subprocess.check_output(cmd, shell=True)
    end = os.times()
    #print end[4] - start[4]

    #lets get data from the output video
    cmd = "ffprobe -show_format " + output_url
    ls_output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

    #file size in MB
    file_size = (int(re.search('size=(\d*)', ls_output).group(1))) / (1024*1024)
    duration = float(re.search('duration=([+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?)', ls_output).group(1))
    #print file_size

    #update the data with additional/modified info 
    data["url"] = input_url
    data.update({'container':container})
    data.update({'ourl':output_url})
    data.update({'real_size':file_size})
    data.update({'real_time':end[4]-start[4]})
    data.update({'duration':duration})
    job_data = Counter(data)  

    # save the results
    try:
        result = Result(
            result_all=job_data
        )
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        errors.append("Unable to add item to database.")
        return {"error": errors}

   
#########r
# routes #
##########

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('et.html')


@app.route('/start', methods=['POST'])
def get_counts():
    # get url
    data = json.loads(request.data.decode())
    url = data["url"]
    data.update({'estimated_time':0}) 
    data.update({'estimated_size':0})
    # form URL, id necessary
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=transcode_and_save_mesurments, args=(data,), result_ttl=5000
    )
    # return created job id
    return job.get_id()


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_all.items(),
            key=operator.itemgetter(1),
            reverse=True
        )
        return jsonify(results)
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run(debug=True)
