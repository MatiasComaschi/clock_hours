import os
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta, timezone
from flask_pymongo import PyMongo
from flask import redirect, url_for, Flask, render_template, request

app = Flask(__name__)
app.config['MONGO_URI'] = os.environ.get("MONGODB_URI")
mongo = PyMongo(app)
db = mongo.db
Bootstrap(app)


def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


app.jinja_env.filters['local_time'] = utc_to_local


def total_hours(x):
    total = 0
    for data in x:
        total += data
    return round(total, 3)


app.jinja_env.filters['total_hours_calc'] = total_hours


@app.route('/')
def check_time():  # put application's code here
    # wb.save(filename=dest_filename)
    return render_template('checktime.html')


# this one will creat collection and insert to mongo collection
@app.route('/checkin', methods=['POST', 'GET'])
def check_in():
    user = request.form['name']
    now = datetime.utcnow()
    current_time = now.strftime("%A %d/%m/%Y")
    time_of_day = now.strftime('%H:%M:%S')
    if request.method == 'POST':
        if 'IN' in request.form:
            db.clockhours.insert_one(
                {'_id': current_time + " " + user, 'Date': current_time,
                 'Employee_Name': user,
                 'clock_in': {"hour": time_of_day,
                              "number_format": str(round((float(
                                  time_of_day[0:2]) / 24 + float(
                                  time_of_day[3:5]) / 1440), 2))},
                 'clock_out': {
                     "hour": '0',
                     "number_format": '0'
                 }})
        elif 'OUT' in request.form:
            db.clockhours.find_one_and_update({'_id': current_time + " " + user},
                                              {"$set":
                                                   {"clock_out":
                                                        {"hour": time_of_day,
                                                         "number_format": str(round((float(
                                                             time_of_day[0:2]) / 24 + float(
                                                             time_of_day[3:5]) / 1440), 2))}
                                                    }
                                               }
                                              )
        elif 'INFO' in request.form:
            return redirect(url_for('show_hours', name=user))
    return render_template('success.html', user=user, time=datetime.utcnow())


# this is will read data from mongo db
@app.route('/info/<name>', methods=['POST', 'GET'])
def show_hours(name):
    user = name
    data = db.clockhours.find({'Employee_Name': user})
    return render_template('hour_wages.html', name=user, datas=data)


if __name__ == '__main__':
    app.run(debug=True)
