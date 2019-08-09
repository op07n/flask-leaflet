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
        fault_dict['traces'] = [(t.trace_lat, t.trace_lon) for t in f.fault_traces]
        fault_traces.append(fault_dict)
    return render_template('index.html', fault_traces=fault_traces)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db.create_all()
        make_data(db, sys.argv[1])
    else:
        app.run(host="0.0.0.0", debug=True)

