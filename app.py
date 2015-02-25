from flask import Flask, render_template, request, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from rq import Queue
from rq.job import Job
from worker import conn
#from transcode import transcode_and_save_mesurments 
import operator
import os
import requests
import re
import json
import time
import nltk
import subprocess 

#################
# configuration #
#################

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)
q = Queue(connection=conn)

from models import Result

#helper

def transcode_and_save_mesurments(cmd,url):

    errors = []

    try:
      #r = requests.get(url)
      print cmd
    except:
        errors.append(
            "Unable to get cmd. Please make sure it's valid and try again."
        )
        return {"error": errors}

    #simulate transcoding 
    #time.sleep(5)
    start = os.times()
    ls_output = subprocess.check_output(cmd, shell=True)
    end = os.times()
    print start[4] - end[4]
    
    #print ls_output

    # text processing
    #raw = BeautifulSoup(r.text).get_text()
    #nltk.data.path.append('./nltk_data/')  # set the path
    #tokens = nltk.word_tokenize(raw)
    #text = nltk.Text(tokens)

    # remove punctuation, count raw words
    #nonPunct = re.compile('.*[A-Za-z].*')
    #raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter({'Estimated': 0, 'Real': end[4] - start[4]})    #Counter(raw_words) 

    # stop words
    #no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter({'Estimated': 0, 'Real': end[4] - start[4]})  #Counter(no_stop_words)
    print no_stop_words_count
    print cmd

    # save the results
    try:
        result = Result(
            url=url,
            result_all=raw_word_count,
            result_no_stop_words=no_stop_words_count
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
    cmd = "ffmpeg  -i " + "/home/tdeneke/easytrans/easytrans/videos/elephants_dream_1080p.h264" + " -c:v " + data["codec"] + " -preset " + data["preset"] + " -s " + data["resolution"] + " -r " + data["framerate"] + " -b:v " + data["bitrate"] + " -y " + "/home/tdeneke/easytrans/easytrans/videos/output.mp4"  
 
    # form URL, id necessary
    if 'http://' not in url[:7]:
        url = 'http://' + url
    # start job
    job = q.enqueue_call(
        func=transcode_and_save_mesurments, args=(cmd,url,), result_ttl=5000
    )
    # return created job id
    return job.get_id()


@app.route("/results/<job_key>", methods=['GET'])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(
            result.result_no_stop_words.items(),
            key=operator.itemgetter(1),
            reverse=True
        )[:10]
        return jsonify(results)
    else:
        return "Nay!", 202


if __name__ == '__main__':
    app.run(debug=True)
