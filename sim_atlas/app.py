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
    magnitude = db.Column(db.Float, nullable=True)
    slip_rate = db.Column(db.VARCHAR(255), nullable=True)
    recurrence_interval = db.Column(db.Integer, nullable=True)
    video = db.Column(db.VARCHAR(255), nullable=True)
    fault_planes = db.relationship('FaultPlane', back_populates='fault', lazy=True)

    def __init__(self, name, magnitude=None, slip_rate=None, recurrence_interval=None, video=None):
        self.name = name
        self.magnitude = magnitude
        self.slip_rate = slip_rate
        self.recurrence_interval = recurrence_interval
        self.video = video


class FaultPlane(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fault_id = db.Column(db.Integer, db.ForeignKey('fault.id'))
    fault = db.relationship('Fault', back_populates='fault_planes')
    fault_traces = db.relationship('FaultTrace', back_populates='fault_plane')

    def __init__(self, fault):
        self.fault = fault


class FaultTrace(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trace_lat = db.Column(db.Float)
    trace_lon = db.Column(db.Float)
    plane_id = db.Column(db.Integer, db.ForeignKey('fault_plane.id'))
    fault_plane = db.relationship('FaultPlane', back_populates='fault_traces')

    def __init__(self, fault_plane, trace_lat, trace_lon):
        self.fault_plane = fault_plane
        self.trace_lat = trace_lat
        self.trace_lon = trace_lon


def make_data(db, json_file):
    with open(json_file, 'r') as f:
        faults_dict = json.load(f)
    for fault_dict in faults_dict:
        fault = Fault(fault_dict['name'], fault_dict['magnitude'], fault_dict['slip_rate'], fault_dict['recurrence_interval'], fault_dict['video'])
        db.session.add(fault)
        for plane in fault_dict['planes']:
            fault_plane = FaultPlane(fault)
            db.session.add(fault_plane)
            for trace_lat, trace_lon in plane:
                fault_trace = FaultTrace(fault_plane, trace_lat, trace_lon)
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
        fault_dict['slip_rate'] = f.slip_rate
        fault_dict['magnitude'] = f.magnitude
        fault_dict['recurrence_interval'] = f.recurrence_interval
        fault_dict['planes'] = [[[t.trace_lat, t.trace_lon] for t in p.fault_traces] for p in f.fault_planes]
        fault_traces.append(fault_dict)
    # fault_traces = [{"name": "Albury", "bounds": [[[-44.0338, 170.7133], [-44.198, 170.8078], [-44.2307, 170.71], [-44.0664, 170.6157]]]}, {"name": "HawkeBay4", "bounds":  [[[-39.0785, 177.4993], [-39.1078, 177.4733], [-39.0008, 177.2354], [-38.9716, 177.2615]], [[-39.1086, 177.4727], [-39.1561, 177.4482], [-39.0491, 177.2102], [-39.0016, 177.2349]], [[-39.1568, 177.4476], [-39.1795, 177.4233], [-39.0725, 177.1853], [-39.0499, 177.2096]]]}]
    return render_template('index.html', fault_traces=fault_traces)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db.create_all()
        make_data(db, sys.argv[1])
    else:
        app.run(host="0.0.0.0", debug=True)

