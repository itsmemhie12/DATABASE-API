from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.exc import IntegrityError
from sqlalchemy import join
from sqlalchemy.sql import select
import requests
import csv
from sqlite3 import Error
import numpy as np
import csv

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'INGdatabase.db') #Creating database using sqlite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Creating 3 database for Manager, It_Custodian and ApplicationData
class Manager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    manager_key = db.Column(db.String(50), unique = True)   # Corporate key which stored all data based on corporate key
    manager_name = db.Column(db.String(50))

class It_custodian(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    it_custodian_key = db.Column(db.String(50))
    it_custodian_name = db.Column(db.String(50))
    manager_name = db.Column(db.String(50))
    manager_key = db.Column(db.String(50), db.ForeignKey(Manager.manager_key))

class ApplicationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    a_description = db.Column(db.Integer)
    a_ing_ci_monitored_by = db.Column(db.String(100))
    it_custodian_ck = db.Column(db.String(100)) #It is the same as corporate key for the IT_custodian
    app_name = db.Column(db.String(100))
    itcustodian_name = db.Column(db.String(100))
    class_name = db.Column(db.String(100))
    app_id = db.Column(db.String(100))
    environment = db.Column(db.String(100))
    is_solution_descr = db.Column(db.String(100))
    server_name = db.Column(db.String(100))


#Route for the Manager to fetch all data that he can only see, based on the Corporate_key/Manager_key he/she had
#And Import it into CSV File name Output
@app.route('/Manager/<Managerkey>', methods = ['GET'])
def Manager_data(Managerkey):
    #Check if the Input Managerkey on api http is on the database
    Mkey = db.session.query(Manager.manager_key)
    Manager_list_key = []
    j = 0
    for j in range(Mkey.count()):
        Manager_list_key.append(Mkey[j][0])
        j += 1
    if Managerkey not in Manager_list_key:
        x = "{} is Wrong Corporate Key, Please type the correct Corporate Key!!".format(Managerkey)
        return jsonify({'message' : x})
    #Query the name of manager based on the Manager Table using Manager_key/Corporate_key
    else:
        Managername = db.session.query(Manager.manager_name).filter(Manager.manager_key == Managerkey).first()
        name = Managername[0]
        #Query the name of It_cis based on the Manager Table using Manager_key/Corporate_key
        key= db.session.query(It_custodian.it_custodian_key).filter(It_custodian.manager_name == name).all()
        # Creating a list of all it_custodian_key coming from the query
        key_list = []
        i = 0
        for i in range(len(key)):
            key_list.append(key[i][0])
            i += 1
        # Deleting all the Duplicate inside the key_list
        key_list = list(dict.fromkeys(key_list))
        # Query all the data from the ApplicationData based on the Corporate_key of Manager
        output = []
        for manager_it_key in key_list:
            AppData = ApplicationData.query.filter_by(it_custodian_ck = manager_it_key).all()
            itper_data = []
            for data in AppData:
                AppData = {}
                AppData['a_description'] = data.a_description
                AppData['a_ing_ci_monitored_by'] = data.a_ing_ci_monitored_by
                AppData['it_custodian_ck'] = data.it_custodian_ck
                AppData['app_name'] = data.app_name
                AppData['itcustodian_name'] = data.itcustodian_name
                AppData['class_name'] = data.class_name
                AppData['app_id'] = data.app_id
                AppData['environment'] = data.environment
                AppData['is_solution_descr'] = data.is_solution_descr
                AppData['server_name'] = data.server_name
                itper_data.append(AppData)
            output.append(itper_data)
        # Create a Message if there's no data in thee corporate key
        if output == []:
            return jsonify({'{} Data'.format(name) : "No Data For {}".format(name)})
        else:
            return jsonify({'{} Data'.format(name) : output})

@app.route('/Manager/<Managerkey>/download', methods = ['GET'])
def data(Managerkey):
    #Check if the Input Managerkey on api http is on the database
    Mkey = db.session.query(Manager.manager_key)
    Manager_list_key = []
    j = 0
    for j in range(Mkey.count()):
        Manager_list_key.append(Mkey[j][0])
        j += 1
    if Managerkey not in Manager_list_key:
        x = "{} is Wrong Corporate Key, Please type the correct Corporate Key!!".format(Managerkey)
        return jsonify({'message' : x})
    #Query the name of manager based on the Manager Table using Manager_key/Corporate_key
    else:
        Managername = db.session.query(Manager.manager_name).filter(Manager.manager_key == Managerkey).first()
        name = Managername[0]
        #Query the name of It_cis based on the Manager Table using Manager_key/Corporate_key
        key= db.session.query(It_custodian.it_custodian_key).filter(It_custodian.manager_name == name).all()
        # Creating a list of all it_custodian_key coming from the query
        key_list = []
        i = 0
        for i in range(len(key)):
            key_list.append(key[i][0])
            i += 1
        # Deleting all the Duplicate inside the key_list
        key_list = list(dict.fromkeys(key_list))
        # Query all the data from the ApplicationData based on the Corporate_key of Manager
        output = []
        for manager_it_key in key_list:
            AppData = ApplicationData.query.filter_by(it_custodian_ck = manager_it_key).all()
            itper_data = []
            for data in AppData:
                AppData = {}
                AppData['a_description'] = data.a_description
                AppData['a_ing_ci_monitored_by'] = data.a_ing_ci_monitored_by
                AppData['it_custodian_ck'] = data.it_custodian_ck
                AppData['app_name'] = data.app_name
                AppData['itcustodian_name'] = data.itcustodian_name
                AppData['class_name'] = data.class_name
                AppData['app_id'] = data.app_id
                AppData['environment'] = data.environment
                AppData['is_solution_descr'] = data.is_solution_descr
                AppData['server_name'] = data.server_name
                itper_data.append(AppData)
            output.append(itper_data)
        # Create a Message if there's no data in thee corporate key
        if output == []:
            return jsonify({'{} Data'.format(name) : "No Data For {}".format(name)})
        else:
            #Code for exporting data from dabase to csv files with a file name output
            file_name = "output.csv"
            data = output
            with open(file_name, 'w', newline = "") as f:
                fieldnames = ["a_description", "a_ing_ci_monitored_by", "it_custodian_ck","app_name", "itcustodian_name","class_name","app_id","environment","is_solution_descr","server_name"]
                thewriter = csv.DictWriter(f, fieldnames = fieldnames)
                thewriter.writeheader()
                for item in data:
                    for dict_data in item:
                        thewriter.writerow(dict_data)
            return jsonify({'Message' : "The Csv File is already Created!!"})

#Route for the It_custodian to fetch all data that he can only see, based on the Corporate_key/It_custodian_key he had.
@app.route('/It_custodian/<it_custodian_uid>' , methods =['GET'])
def get_all_data_under_ItCustodian(it_custodian_uid):
    #Check if the Input Managerkey on api http is on the database
    itkey = db.session.query(It_custodian.it_custodian_key)
    It_list_key = []
    j = 0
    for j in range(itkey.count()):
        It_list_key.append(itkey[j][0])
        j += 1
    if it_custodian_uid not in It_list_key:
        x = "{} is Wrong Corporate Key, Please type the correct Corporate Key!!".format(it_custodian_uid)
        return jsonify({'message' : x})
    else:
        AppData = ApplicationData.query.filter_by(it_custodian_ck = it_custodian_uid).all()
        # Query all the data from the ApplicationData based on the Corporate_key/It_custodian_key
        output = []
        for data in AppData:
            AppData = {}
            AppData['a_description'] = data.a_description
            AppData['a_ing_ci_monitored_by'] = data.a_ing_ci_monitored_by
            AppData['it_custodian_ck'] = data.it_custodian_ck
            AppData['app_name'] = data.app_name
            AppData['itcustodian_name'] = data.itcustodian_name
            AppData['class_name'] = data.class_name
            AppData['app_id'] = data.app_id
            AppData['environment'] = data.environment
            AppData['is_solution_descr'] = data.is_solution_descr
            AppData['server_name'] = data.server_name
            output.append(AppData)

        if output == []:
            return jsonify({'{} Data'.format(data.itcustodian_name) : "No Data For {}".format(data.itcustodian_name)})
        else:
            return jsonify({'{} Data'.format(data.itcustodian_name) : output})

#Route for the It_custodian to fetch all data that he can only see, based on the Corporate_key/It_Custodian_key he/she had
#And Import it into CSV File name Output
@app.route('/It_custodian/<it_custodian_uid>/download' , methods =['GET'])
def CSVFiles_ItCustodian(it_custodian_uid):
    #Check if the Input Managerkey on api http is on the database
    itkey = db.session.query(It_custodian.it_custodian_key)
    It_list_key = []
    j = 0
    for j in range(itkey.count()):
        It_list_key.append(itkey[j][0])
        j += 1
    if it_custodian_uid not in It_list_key:
        x = "{} is Wrong Corporate Key, Please type the correct Corporate Key!!".format(it_custodian_uid)
        return jsonify({'message' : x})
    else:
        AppData = ApplicationData.query.filter_by(it_custodian_ck = it_custodian_uid).all()
        # Query all the data from the ApplicationData based on the Corporate_key/It_custodian_key
        output = []
        for data in AppData:
            AppData = {}
            AppData['a_description'] = data.a_description
            AppData['a_ing_ci_monitored_by'] = data.a_ing_ci_monitored_by
            AppData['it_custodian_ck'] = data.it_custodian_ck
            AppData['app_name'] = data.app_name
            AppData['itcustodian_name'] = data.itcustodian_name
            AppData['class_name'] = data.class_name
            AppData['app_id'] = data.app_id
            AppData['environment'] = data.environment
            AppData['is_solution_descr'] = data.is_solution_descr
            AppData['server_name'] = data.server_name
            output.append(AppData)

        if output == []:
            return jsonify({'{} Data'.format(data.itcustodian_name) : "No Data For {}".format(data.itcustodian_name)})
        else:
            #Code for exporting data from dabase to csv files with a file name output
            file_name = "output.csv"
            data = output
            with open(file_name, 'w', newline = "") as f:
                fieldnames = ["a_description", "a_ing_ci_monitored_by", "it_custodian_ck","app_name", "itcustodian_name","class_name","app_id","environment","is_solution_descr","server_name"]
                thewriter = csv.DictWriter(f, fieldnames = fieldnames)
                thewriter.writeheader()
                for item in data:
                    thewriter.writerow(item)
            return jsonify({'Message' : "The Csv File is already Created!!"})

#Creating route for creating Manager in Manager Table
@app.route('/Manager', methods=['POST'])
def create_manager():
    data = request.get_json()
    try:
        new_manager = Manager(manager_key=data['manager_key'], manager_name=data['manager_name'])
        db.session.add(new_manager)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message' : 'The Manager Is already on the database!'})
    return jsonify({'message' : 'New Manager has been created!'})


#Creating route for creating IT_Custodian in IT_Custodian Table
@app.route('/It_custodian', methods=['POST'])
def create_it_custodian():
    data = request.get_json()
    try:
        new_it_custodian = It_custodian(it_custodian_key=data['it_custodian_key'], it_custodian_name=data['it_custodian_name'],
                            manager_name=data['manager_name'])
        db.session.add(new_it_custodian)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message' : 'The It_custodian Is already on the database!'})
    return jsonify({'message' : 'New IT_custodian has been created!'})

#Creating route for creating Application Data in ApplicationData Table
@app.route('/ApplicationData', methods=['POST'])
def create_ApplicationData():
    app = request.get_json()
    new_Data_Application = ApplicationData(
                    a_description = app['a_description'],
                    a_ing_ci_monitored_by = app['a_ing_ci_monitored_by'],
                    it_custodian_ck = app['it_custodian_ck'],
                    app_name = app['app_name'],
                    itcustodian_name = app['itcustodian_name'],
                    class_name = app['class_name'],
                    app_id = app['app_id'],
                    environment = app['environment'],
                    is_solution_descr = app['is_solution_descr'],
                    server_name = app['server_name'])
    db.session.add(new_Data_Application)
    db.session.commit()
    return jsonify({'message' : 'New Data has been Created!'})



if __name__ == '__main__':
    app.run(debug=True)
