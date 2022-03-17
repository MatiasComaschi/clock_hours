import os
import time

from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta, timezone
from flask_pymongo import PyMongo
from flask import redirect, url_for, Flask, render_template, request

app = Flask(__name__)
#
app.config['MONGO_URI'] =os.environ.get("MONGODB_URI")
mongo = PyMongo(app)
db = mongo.db
Bootstrap(app)


def hour_beautify(x):
    return x.strftime('%H:%M:%S')


app.jinja_env.filters['hour_convert'] = hour_beautify


def date_beautify(x):
    return x.strftime("%A %d/%m/%Y")


app.jinja_env.filters['date_convert'] = date_beautify


@app.route('/')
def check_time():  # put application's code here
    return render_template('checktime.html')


# this one will creat collection and insert to mongo collection
@app.route('/checkin', methods=['POST', 'GET'])
def check_in():
    user = request.form['name']
    now = datetime.utcnow()
    current_time = (now - (now-datetime.now())).strftime("%A %m/%d")
    if request.method == 'POST':
        if 'IN' in request.form:
            db.clockhours.insert_one(
                {'_id': current_time + " " + user, 'Date': current_time,
                 'Employee_Name': user,
                 'clock_in': {"hour_UTC": now, "offset": str(now - datetime.now())
                              },
                 'clock_out': {
                     "hour_UTC": '0',
                     "offset": str(now - datetime.now())
                 }})
        elif 'OUT' in request.form:
            db.clockhours.find_one_and_update({'_id': current_time + " " + user},
                                              {"$set":
                                                   {"clock_out":
                                                        {"hour_UTC": now, "offset": str(now - datetime.now())
                                                         # "number_format": str(round((float(
                                                         #     time_of_day[0:2]) / 24 + float(
                                                         #     time_of_day[3:5]) / 1440), 2)),
                                                         }
                                                    }
                                               }
                                              )
        elif 'INFO' in request.form:
            return redirect(url_for('show_hours', name=user))
    return render_template('success.html', user=user, time=datetime.utcnow(), offset=datetime.utcnow() - datetime.now())


# this is will read data from mongo db
@app.route('/info/<name>', methods=['POST', 'GET'])
def show_hours(name):
    user = name
    data = db.clockhours.find({'Employee_Name': user})
    return render_template('hour_wages.html', name=user, datas=data, offset=datetime.utcnow() - datetime.now())


if __name__ == '__main__':
    app.run(debug=True)
