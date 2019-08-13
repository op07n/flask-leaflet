import json
import sys
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flask_admin:flask_admin@localhost/sim_atlas'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Fault(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.VARCHAR(255), nullable=False, unique=True)
    video = db.Column(db.VARCHAR(255), nullable=True)
    fault_traces = db.relationship('FaultTrace', back_populates='fault', lazy=True)

    def __init__(self, name, video=None):
        self.name = name
        self.video = video


class FaultTrace(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trace_lat = db.Column(db.Float)
    trace_lon = db.Column(db.Float)
    fault_id = db.Column(db.Integer, db.ForeignKey('fault.id'))
    fault = db.relationship('Fault', back_populates='fault_traces')

    def __init__(self, fault, trace_lat, trace_lon):
        self.fault = fault
        self.trace_lat = trace_lat
        self.trace_lon = trace_lon


def make_data(db, json_file):
    with open(json_file, 'r') as f:
        faults_dict = json.load(f)
    for fault_dict in faults_dict:
        fault = Fault(fault_dict['name'], fault_dict['video'])
        db.session.add(fault)
        for trace_lat, trace_lon in fault_dict['traces']:
            fault_trace = FaultTrace(fault, trace_lat, trace_lon)
            db.session.add(fault_trace)
    db.session.commit()


@app.route("/")
def get_faults():
    faults = Fault.query.all()
    fault_traces = []
    for f in faults:
        fault_dict = {}
        fault_dict['name'] = f.name
        fault_dict['video'] = f.video
        fault_dict['traces'] = [[t.trace_lat, t.trace_lon] for t in f.fault_traces]
        fault_traces.append(fault_dict)
    with open("/home/melody/flask-leaflet/sim_atlas/static/data/v18p6_rerun_all_faults_bounds.json", 'r') as f:
        fault_traces = json.load(f)
    #fault_traces = [{"name": "Albury", "bounds": [[[-44.0338, 170.7133], [-44.198, 170.8078], [-44.2307, 170.71], [-44.0664, 170.6157]]]}, {"name": "HawkeBay4", "bounds":  [[[-39.0785, 177.4993], [-39.1078, 177.4733], [-39.0008, 177.2354], [-38.9716, 177.2615]], [[-39.1086, 177.4727], [-39.1561, 177.4482], [-39.0491, 177.2102], [-39.0016, 177.2349]], [[-39.1568, 177.4476], [-39.1795, 177.4233], [-39.0725, 177.1853], [-39.0499, 177.2096]]]}]
    return render_template('index.html', fault_traces=fault_traces)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db.create_all()
        make_data(db, sys.argv[1])
    else:
        app.run(host="0.0.0.0", debug=True)

