# 1. import Flask
from flask import Flask, jsonify, render_template
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine




engine = create_engine("sqlite:///belly_button_biodiversity.sqlite", echo=False)
Base = automap_base()
Base.prepare(engine, reflect=True)


otu = Base.classes.otu
samp = Base.classes.samples
meta = Base.classes.samples_metadata

session = Session(engine)

# 2. Create an app, being sure to pass __name__
app = Flask(__name__)

@app.route("/")
def welcome():
    return render_template("index.html")

# 3. Define what to do when a user hits the index route
@app.route("/names")
def home():
    qry = session.query(samp).first()
    samples_list = [e for e in qry.__dict__]
    samples_list.pop(0)
    samples_list.pop(samples_list.index('otu_id'))
    dic = {}
    num = []
    for e in samples_list:
        dic[int(e[3:])] = e
        num.append(int(e[3:]))
    num.sort(key=int)
    n_samples = []
    for e in num:
        n_samples.append(dic[e])
    return jsonify(n_samples)

# 4. Define what to do when a user hits the /about route
@app.route("/otu")
def about():
    qry = session.query(otu.lowest_taxonomic_unit_found).all()
    fe = [e[0] for e in qry]
    return jsonify(fe)

@app.route("/wfreq/<sample>")
def tobs(sample):
    qry = session.query(meta).all()
    rr = [e.__dict__ for e in qry]
    rr
    washed = {}
    for e in rr:
        if "BB_"+str(e["SAMPLEID"]) == sample:
            washed["Washes Per Week"] = e["WFREQ"]
            break
    return jsonify(washed)

@app.route("/metadata/<sample>")
def sas(sample):
    qry = session.query(meta).all()
    rr = [e.__dict__ for e in qry]
    sample_info = []
    for e in rr:
        if sample == "BB_"+str(e["SAMPLEID"]):
            new = {}
            new["AGE"] = e["AGE"]
            new["BBTYPE"] = e["BBTYPE"]
            new["ETHNICITY"] = e["ETHNICITY"]
            new["GENDER"] = e["GENDER"]
            new["LOCATION"] = e["LOCATION"]
            new["SAMPLEID"] = e["SAMPLEID"]
            sample_info.append(new)
            break
    return jsonify(sample_info)

@app.route("/samples/<sample>")
def meh(sample):
    sss = session.query(samp).all()
    der = {}
    for h in sss:
        f = h.__dict__
        der[f["otu_id"]] = f[sample]
    ids = []
    values = []
    for e in der:
        values.append(int(der[e]))
    values = sorted(values, key=int, reverse = True)
    k = 0
    for v in values:
        for d in der:
            if der[d] == v and d not in ids:
                ids.append(d)
                break
        k+=1
        if k ==10:
            break
    fin = {}
    fin["otu_ids"] = ids
    fin["sample_values"] = values[:10]
    return jsonify(fin)
if __name__ == "__main__":
    app.run(debug=True)