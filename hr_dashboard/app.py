import os
import seaborn as sns
import pandas as pd
import numpy as np
import math
import types
import colorsys
from scipy import stats
import matplotlib
import matplotlib.pyplot as plt  
matplotlib.style.use('ggplot')
plt.style.use('seaborn-talk')
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import ListedColormap
import pylab
from plotly.graph_objs import *
import warnings
import matplotlib.cbook
warnings.filterwarnings("ignore",category=matplotlib.cbook.mplDeprecation)
import sqlalchemy
from sqlalchemy import create_engine, MetaData, inspect, func, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import DisconnectionError
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from api2pdf import Api2Pdf
import json
import urllib
import requests
import pdfkit
import datetime
import time
import random
import threading
from dateutil.parser import parse
from collections import defaultdict, ChainMap, OrderedDict
from celery import Celery
from celery import uuid
import redis
pd.options.mode.chained_assignment = None

### Color Schemes ##
from matplotlib import cm
current_palette = sns.color_palette("muted", n_colors=30)
cmap1 = cm.get_cmap('gist_rainbow')
cmap2 = cm.get_cmap('rainbow')
cs1 = cm.Dark2(np.arange(40))
cs2 = cm.Paired(np.arange(40))





#################################################
# Flask Setup
#################################################
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(PROJECT_ROOT,'../hr_dashboard')
STATIC_DIR = os.path.join(PROJECT_DIR,'static/')
IMG_DIR = os.path.join(STATIC_DIR,'img/')
PDF_STYLE_DIR = os.path.join(STATIC_DIR,'pdf_style/')

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

####### FOR HEROKU DEPLOYMENT ONLY ########:
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

####### FOR LOCAL USE ONLY ########:
# from config import my_secret_key
# app.config['SECRET_KEY'] = my_secret_key





#################################################
# Api2Pdf Setup
#################################################
USERAGENT = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

####### FOR HEROKU DEPLOYMENT ONLY ########:
API2PDF_API_KEY = os.environ.get('API2PDF_apikey')

####### FOR LOCAL USE ONLY ########:
# from APIkeys import apikey
# API2PDF_API_KEY = apikey





#################################################
# Celery & Redis Config
#################################################
####### FOR HEROKU DEPLOYMENT ONLY ########:
app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL')
app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL')

####### FOR LOCAL USE ONLY ########:
# from config import my_redis_url
# app.config['CELERY_BROKER_URL'] = my_redis_url
# app.config['CELERY_RESULT_BACKEND'] = my_redis_url

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
# celery.conf.update(app.config)




#################################################
# SQL Database Models, Config & Setup
#################################################
SQLCONNECTION = 'sqlite:///Dental_Magic_HR_v9.sqlite'
app.config['SQLALCHEMY_DATABASE_URI'] = SQLCONNECTION
db = SQLAlchemy(app)
engine = db.create_engine(SQLCONNECTION, pool_recycle=3600, echo=False)
session = Session(engine)

class Employee_Data(db.Model):
    __tablename__ = 'employee_data'
    ID = db.Column(db.Integer, primary_key=True)    
    LastName = db.Column(db.Text)
    FirstName = db.Column(db.Text)    
    EmployeeNumber = db.Column(db.Integer)
    MarriedID = db.Column(db.Integer)
    MaritalStatusID = db.Column(db.Integer)
    GenderID = db.Column(db.Integer)
    EmpStatusID = db.Column(db.Integer)
    DeptID = db.Column(db.Integer)
    PerfScoreID = db.Column(db.Integer)
    Age = db.Column(db.Integer)
    PayRate = db.Column(db.Float)
    State = db.Column(db.Text)    
    Zip = db.Column(db.Integer)
    DOB = db.Column(db.Text)
    Sex = db.Column(db.Text) 
    MaritalDesc = db.Column(db.Text)
    CitizenDesc = db.Column(db.Text)
    Hispanic_Latino = db.Column(db.Text)
    RaceDesc = db.Column(db.Text)
    HireDate = db.Column(db.Text)
    DaysEmployed = db.Column(db.Integer)
    TerminationDate = db.Column(db.Text, nullable=True)
    ReasonForTerm = db.Column(db.Text)
    EmploymentStatus = db.Column(db.Text)
    Department = db.Column(db.Text)
    Position = db.Column(db.Text)
    ManagerName = db.Column(db.Text)
    EmployeeSource = db.Column(db.Text)
    PerformanceScore = db.Column(db.Text)

class Recruiting_Costs(db.Model):
    __tablename__ = 'recruiting_costs'    
    ID = db.Column(db.Integer, primary_key=True)
    EmploymentSource = db.Column(db.Text)
    January_2018 = db.Column(db.Integer)
    February_2018 = db.Column(db.Integer)
    March_2018 = db.Column(db.Integer)
    April_2018 = db.Column(db.Integer)
    May_2018 = db.Column(db.Integer)
    June_2018 = db.Column(db.Integer)
    July_2018 = db.Column(db.Integer)
    August_2018 = db.Column(db.Integer)
    September_2018 = db.Column(db.Integer)
    October_2018 = db.Column(db.Integer)
    November_2018 = db.Column(db.Integer)
    December_2018 = db.Column(db.Integer)

db.create_all()
db.session.commit()

	


	
#################################################
# Global Variables
#################################################
_index_src_dict = None
_demo_src_dict = None 
_tal_src_dict = None
_attr_src_dict = None
_recr_src_dict = None





#################################################
# Celery Tasks
#################################################
@celery.task(bind=True)
def getAllImages_task(self):
	"""Background task that creates index page images."""
	self.update_state(state='PROGRESS', meta={'current': 50, 'total': 50, 'status': 'Loading... Please wait...'})
	img_src_dict = getAllImgSources()	

	return {'current': 100, 'total': 100, 'status': 'Done!', 'result': img_src_dict}
	

@celery.task(bind=True)
def getDemographicsImages_task(self):
	"""Background task that creates Demographics page images."""
	self.update_state(state='PROGRESS', meta={'status': ''})
	img_src_dict = getDemographicsImgSources()

	return {'status': 'Done', 'result': img_src_dict}	
	

@celery.task(bind=True)
def getRecruitingImages_task(self):
	"""Background task that creates Recruiting page images."""
	self.update_state(state='PROGRESS', meta={'status': ''})
	img_src_dict = getRecruitingImgSources()

	return {'status': 'Done', 'result': img_src_dict}
	
	
@celery.task(bind=True)
def getAttritionImages_task(self):
	"""Background task that creates Attrition page images."""
	self.update_state(state='PROGRESS', meta={'status': ''})
	img_src_dict = getAttritionImgSources()

	return {'status': 'Done', 'result': img_src_dict}	
	

@celery.task(bind=True)
def getTalentImages_task(self):
	"""Background task that creates Talent page images."""
	self.update_state(state='PROGRESS', meta={'status': ''})
	img_src_dict = getTalentImgSources()

	return {'status': 'Done', 'result': img_src_dict}	
		
	
	
		

#################################################
# Flask Routes
#################################################
@app.route('/', methods=['GET', 'POST'])
def index():
	"""Render Home/Index Page"""
	global _index_src_dict
	if request.method == 'POST':
		_index_src_dict = request.get_json(force=True)
		return ('', 204)
	else:
		if _index_src_dict is None:
			return redirect(url_for('loading'))	
		else:
			src_dict = _index_src_dict
			return render_template('index.html', src_dict=src_dict)
			

@app.route("/demographics", methods=['GET', 'POST'])
def demographics():
	"""Render Employee Demographics Page"""
	global _demo_src_dict
	if request.method == 'POST':
		_demo_src_dict = request.get_json(force=True)
		return ('', 204)
	else:
		if _demo_src_dict is None:	
			task_func = 'getDemographicsImages_task'
			page = 'demographics'
			return render_template('loading2.html', task_func=task_func, page=page)				
		else:
			src_dict = _demo_src_dict
			return render_template('demographics.html', src_dict = src_dict)			
		
	
@app.route("/recruiting", methods=['GET', 'POST'])
def recruiting():
	"""Render Recruitment Page"""
	global _recr_src_dict
	if request.method == 'POST':
		_recr_src_dict = request.get_json(force=True)
		return ('', 204)
	else:
		if _recr_src_dict is None:	
			task_func = 'getRecruitingImages_task'
			page = 'recruiting'
			return render_template('loading2.html', task_func=task_func, page=page)				
		else:
			src_dict = _recr_src_dict
			return render_template('recruiting.html', src_dict = src_dict)
	
	
@app.route("/attrition", methods=['GET', 'POST'])
def attrition():
	"""Render Employee Retention & Attrition Page"""
	global _attr_src_dict
	if request.method == 'POST':
		_attr_src_dict = request.get_json(force=True)
		return ('', 204)
	else:
		if _attr_src_dict is None:	
			task_func = 'getAttritionImages_task'
			page = 'attrition'
			return render_template('loading2.html', task_func=task_func, page=page)				
		else:
			src_dict = _attr_src_dict
			return render_template('attrition.html', src_dict = src_dict)

		
@app.route("/talent", methods=['GET', 'POST'])
def talent():
	"""Render HR Talent Management Page"""
	global _tal_src_dict
	if request.method == 'POST':
		_tal_src_dict = request.get_json(force=True)
		return ('', 204)
	else:
		if _tal_src_dict is None:	
			task_func = 'getTalentImages_task'
			page = 'talent'
			return render_template('loading2.html', task_func=task_func, page=page)				
		else:
			src_dict = _tal_src_dict	
			return render_template('talent.html', src_dict = src_dict)

		
@app.route("/glossary")
def glossary():
	"""Render HR Glossary Page"""
	plt.close('all')
	
	return render_template("glossary.html")	
	
			
@app.route('/loading')
def loading():
	"""Render Intro Loader Page"""

	return render_template("loading.html")	
	
	
@app.route('/getAllImagesTask', methods=['POST'])
def getAllImagesTask():
	task = getAllImages_task.apply_async()
	
	return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}	
	
	
@app.route('/status/<task_id>')
def taskstatus(task_id):
	task = getAllImages_task.AsyncResult(task_id)
	if task.state == 'PENDING':
		response = {
			'state': task.state,
			'current': 0,
			'total': 1,
			'status': 'Loading Home Page...'
		}
	elif task.state != 'FAILURE':
		response = {
			'state': task.state,
			'current': task.info.get('current', 0),
			'total': task.info.get('total', 1),
			'status': task.info.get('status', '')
		}
		if 'result' in task.info:
				response['result'] = task.info['result']	
	else:
		# something went wrong in the background job
		response = {
			'state': task.state,
			'current': 1,
			'total': 1,
			'status': str(task.info),  # the exception raised
		}
		
	return jsonify(response)


@app.route('/getPageImagesTask/<func>', methods=['POST'])
def getPageImagesTask(func):
	myPageTask = globals()[func]
	task = myPageTask.apply_async()
	
	return jsonify({}), 202, {'Location': url_for('getTaskStatus', task_id=task.id, func=func)}
	

@app.route('/status/<task_id>/<func>')
def getTaskStatus(task_id, func):
	myPageTask = globals()[func]
	task = myPageTask.AsyncResult(task_id)
	if task.state == 'PENDING':
		response = {
			'state': task.state,
			'status': 'Pending...'
		}
	elif task.state != 'FAILURE':
		response = {
			'state': task.state,
			'status': task.info.get('status', '')
		}
		if 'result' in task.info:
				response['result'] = task.info['result']	
	else:
		# something went wrong in the background job
		response = {
			'state': task.state,
			'status': str(task.info),  # the exception raised
		}
		
	return jsonify(response)
	

@app.route('/download_pdf/<pageName>')
def download_pdf(pageName):
	"""Download PDF of Selected Page Data"""
	a2p_client = Api2Pdf(API2PDF_API_KEY)
	siteUrlStub = 'https://hr-dashboard1.herokuapp.com/'
	# siteUrlStub = 'http://127.0.0.1:5000/' ### FOR LOCAL PDF TESTING ONLY ###	
	pageUrl = siteUrlStub + pageName
	saveName = pageName
	options = {
		'displayHeaderFooter': 'true',
		'footerTemplate': '<span class=”date”></span><br><span class=”pageNumber”></span>'
	}
	pdf_response = a2p_client.HeadlessChrome.convert_from_url(pageUrl, fileName=saveName, **options)	
	if pdf_response.result['success'] == True:
		pdf_url = pdf_response.result['pdf']
		return redirect(pdf_url, code=302)
	else:
		flash('An error occurred -- unable to download PDF')
		return ('', 204)


@app.route("/demographics_pdf")
def demographics_pdf():
	
	return render_template("demographics_pdf.html")	


@app.route("/recruiting_pdf")
def recruiting_pdf():
	
	return render_template("recruiting_pdf.html")		
		

@app.route("/attrition_pdf")
def attrition_pdf():
	
	return render_template("attrition_pdf.html")	
	

@app.route("/talent_pdf")
def talent_pdf():
	
	return render_template("talent_pdf.html")		
	
	
@app.route("/application-error")
def application_error():
	"""Render App Error Page"""
	
	return render_template("application-error.html")	
	

@app.errorhandler(404)
def not_found_error(error):

    return render_template('404.html'), 404
	
	
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
	
    return render_template('500.html'), 500	

		
	

	
#################################################
# Image/Source Functions
#################################################
def getDataDF(sql):	
	df = pd.read_sql_query(sql, db.session.bind)	
	
	return df	


def getAllImgSources():
	src_dict = {}
	sql_stmnt1 = "Select * from employee_data"
	df = getDataDF(sql_stmnt1)
	sql_stmnt2 = "Select * from recruiting_costs"
	df2 = getRecruitCostsDF(sql_stmnt2)	
	
	costs_df = df2.copy()	
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]	
	allEmp_df = df.copy()

	src_dict.update(src1a = empStatusSrc(allEmp_df))	
	src_dict.update(src2a = deptSrc(current_df))
	src_dict.update(src3a = deptCountSrc(current_df))
	src_dict.update(src4a = positionCountSrc(current_df))
	src_dict.update(src5 = raceDistribSrc(current_df))
	src_dict.update(src6 = racePercentSrc(current_df))
	src_dict.update(src7 = genderCountSrc(current_df))
	src_dict.update(src8 = ageCountSrc(current_df))
	src_dict.update(src9 = maritalDistribSrc(current_df))
	src_dict.update(src10 = raceDistrib2Src(current_df))
	src_dict.update(src11 = genderDistribSrc(current_df))
	src_dict.update(src12 = staffLocalesSrc(current_df))

	src_dict.update(src1b = recruitingSrc(costs_df))
	src_dict.update(src2b = employCosts2018Src(costs_df))
	src_dict.update(src3b = raceEmploySrcSrc(allEmp_df))
	src_dict.update(src4b = genderEmploySrcSrc(allEmp_df))
	
	src_dict.update(src1c = staffPerfSrc(current_df))
	src_dict.update(src2c = staffPerfScoreDistribSrc(current_df))
	src_dict.update(src3c = perfScoreCountSrc(allEmp_df))
	src_dict.update(src4c = deptPerfScoreCountSrc(allEmp_df))
	
	src_dict.update(src1d = termReasonsSrc(allEmp_df))
	src_dict.update(src2d = rftRaceSrc(allEmp_df))
	src_dict.update(src3d = rftMaritalSrc(allEmp_df))
	src_dict.update(src4d = rftGenderSrc(allEmp_df))	

	return src_dict
	

def getDemographicsImgSources():	
	src_dict = {}
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]
	
	src_dict.update(src1 = empStatusSrc(df))
	src_dict.update(src2 = deptSrc(current_df))
	src_dict.update(src3 = deptCountSrc(current_df))
	src_dict.update(src4 = positionCountSrc(current_df))
	src_dict.update(src5 = raceDistribSrc(current_df))
	src_dict.update(src6 = racePercentSrc(current_df))
	src_dict.update(src7 = genderCountSrc(current_df))
	src_dict.update(src8 = ageCountSrc(current_df))
	src_dict.update(src9 = maritalDistribSrc(current_df))
	src_dict.update(src10 = raceDistrib2Src(current_df))
	src_dict.update(src11 = genderDistribSrc(current_df))
	src_dict.update(src12 = staffLocalesSrc(current_df))

	return src_dict
	
	
def getRecruitingImgSources():	
	src_dict = {}
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	sql_stmnt2 = "Select * from recruiting_costs"
	df2 = getRecruitCostsDF(sql_stmnt2)		
	allEmp_df = df.copy()
	costs_df = df2.copy()
	
	src_dict.update(src1 = recruitingSrc(costs_df))
	src_dict.update(src2 = employCosts2018Src(costs_df))
	src_dict.update(src3 = raceEmploySrcSrc(allEmp_df))
	src_dict.update(src4 = genderEmploySrcSrc(allEmp_df))
	
	return src_dict


def getAttritionImgSources():	
	src_dict = {}
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	allEmp_df = df.copy()	
	
	src_dict.update(src1 = termReasonsSrc(allEmp_df))
	src_dict.update(src2 = rftRaceSrc(allEmp_df))
	src_dict.update(src3 = rftMaritalSrc(allEmp_df))
	src_dict.update(src4 = rftGenderSrc(allEmp_df))

	return src_dict


def getTalentImgSources():	
	src_dict = {}
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]	
	allEmp_df = df.copy()	
	
	src_dict.update(src1 = staffPerfSrc(current_df))
	src_dict.update(src2 = staffPerfScoreDistribSrc(current_df))
	src_dict.update(src3 = perfScoreCountSrc(allEmp_df))
	src_dict.update(src4 = deptPerfScoreCountSrc(allEmp_df))

	return src_dict	
	
	
def getRecruitCostsDF(sql):
	df = pd.read_sql_query(sql, db.session.bind)
	new_df = df.copy()
	new_df.drop(['ID'], axis=1, inplace=True)
	costTbl = pd.pivot_table(new_df,index=["EmploymentSource"])
	col_order = ['January_2018', 'February_2018', 'March_2018', 'April_2018', 'May_2018', 'June_2018','July_2018', 'August_2018', 'September_2018', 'October_2018', 'November_2018', 'December_2018']
	newCostTbl = costTbl.reindex(col_order, axis=1)
	
	return newCostTbl
		
	
def deptSrc(df):	
	fig = (df['Department'].value_counts()[0:20].plot(kind='pie',figsize=(8,8),title='Current Departmental Staff',
		autopct='%1.1f%%',colormap=cmap1,label='',fontsize=20)).get_figure()
	img_file = 'dept.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()	
	plt.close()	
	src = '../static/img/dept.png'
	
	return src	
		

def recruitingSrc(df):	
	totalsTbl2018 = df.sum(axis=1)
	top10_2018costs = totalsTbl2018.nlargest(10)
	fig = (top10_2018costs.plot(kind='pie',figsize=(8,8),autopct='%1.1f%%',colormap=cmap2,title='2018 Top 10 Costliest Employment Sources',
		label='',fontsize=20)).get_figure()
	img_file = 'top10recruit.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')	
	plt.clf()	
	plt.close()	
	src = '../static/img/top10recruit.png'
	
	return src	


def staffPerfSrc(df):	
	fig = (df['PerformanceScore'].value_counts()[0:20].plot(kind='pie',figsize=(8,8),autopct='%1.1f%%',colormap=cmap2,
		title='Current Staff Performance Score Results',label='',fontsize=20)).get_figure()
	img_file = 'staffPerf.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')	
	plt.clf()
	plt.close()	
	src = '../static/img/staffPerf.png'
	
	return src
		
	
def termReasonsSrc(df):	   
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	fig =(rft_df['ReasonForTerm'].value_counts()[0:20].plot(kind='barh',figsize=(10,8),colormap=cmap1,title='Reasons For Termination')).get_figure()
	img_file = 'termReasons.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')	
	plt.clf()
	plt.close()
	src = '../static/img/termReasons.png'
	
	return src	
	

def staffLocalesSrc(df):	
	locTbl = pd.crosstab(index=df["Department"], columns=df["State"])
	locTbl.plot(kind="barh",figsize=(15,7),stacked=True,colormap=cmap2,title='Staff Location By Department').legend(bbox_to_anchor=(1,1),fontsize=18)
	ax2 = plt.axes()
	ax2.yaxis.label.set_visible(False)
	for tick in ax2.get_xticklabels():
		tick.set_fontsize(20)
	for tick in ax2.get_yticklabels():
		tick.set_fontsize(20)
	img_file = 'staffLocale.png'
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/staffLocale.png'
	
	return src	
			
	
def empStatusSrc(df):
	employment_status=df.groupby(by='EmploymentStatus').size().sort_values(ascending=False).head(10)
	employment_status=employment_status.reindex(index=['Active','Leave of Absence','Future Start','Voluntarily Terminated','Terminated for Cause'])
	
	employed_total=df['ReasonForTerm'].str.contains('Not applicable').sum()
	termed_total=(employment_status.sum())-employed_total
	data={'CURRENTLY EMPLOYED':employed_total, 'TERMINATED':termed_total}
	employment_status2 = pd.Series(data,index=['CURRENTLY EMPLOYED','TERMINATED'])
	employment_status2.index.name = 'EmploymentStatus2'
	
	pie1Labels = list(employment_status2.index)
	pie1Sizes = list(employment_status2.values)
	pie2Labels = list(employment_status.index)
	pie2Sizes = list(employment_status.values)

	group_names = pie1Labels
	group_size = pie1Sizes
	subgroup_names = pie2Labels
	subgroup_size = pie2Sizes

	fig = plt.figure(figsize=(12.5, 12))
	ax1 = plt.subplot2grid((2,6),(0,4),rowspan=2,colspan=2)
	ax1.axis('equal')
	a, b = [plt.cm.Greens, plt.cm.Oranges]
	# First Ring (outside)
	mypie, _ = ax1.pie(group_size,radius=2.6,labels=group_names,colors=[a(0.6),b(0.6)],textprops=dict(color="gray"),startangle=2)
	plt.setp(mypie, width=0.6, edgecolor='white')
	# Second Ring (Inside)
	mypie2, _ = ax1.pie(subgroup_size,radius=2.6-0.6,labels=subgroup_names,labeldistance=0.3,rotatelabels=True,startangle=2,colors=[a(0.4), a(0.3), a(0.2), b(0.4), b(0.3)])
	plt.setp(mypie2, width=1.5, edgecolor='white')
	plt.margins(0,0)

	ax2 = plt.subplot2grid((2,6),(0,0),rowspan=1,colspan=3)
	plt.pie(pie1Sizes,labels=None,autopct='%1.1f%%',colors=cs1,startangle=2)
	plt.title('')
	plt.legend(labels=pie1Labels, bbox_to_anchor=(0.34,0.89), loc="center left", fontsize=12, bbox_transform=plt.gcf().transFigure)

	ax3 = plt.subplot2grid((2,6),(1,0),rowspan=1,colspan=3)
	plt.pie(pie2Sizes,labels=None,autopct='%1.1f%%',colors=cs2,startangle=2)
	plt.title('Employment Status - All Records')
	plt.legend(labels=pie2Labels, bbox_to_anchor=(0.6,0.18), loc="center right", fontsize=12, bbox_transform=plt.gcf().transFigure)
	plt.tight_layout()
	img_file = 'status.png'	
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/status.png'
	
	return src	

	
def deptCountSrc(df):		
	fig = (df['Department'].value_counts()[0:20].plot(kind='barh',figsize=(10,8),title='Current Staff Count Per Dept',label='',fontsize=20)).get_figure()
	img_file = 'deptCount.png'	
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')	
	plt.clf()
	plt.close()	
	src = '../static/img/deptCount.png'
	
	return src
	
	
def positionCountSrc(df):	
	plt.figure(figsize=(16,8))
	sns.countplot('Position', data=df)
	plt.xticks(rotation = 60, ha='right')
	plt.title('Current Staff Count Per Position')
	plt.tight_layout()
	img_file = 'positionCount.png'	
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/positionCount.png'

	return src
		

def raceDistribSrc(df):	
	g = sns.catplot("RaceDesc", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Staff Racial Distribution")
	img_file = 'raceDistrib.png'	
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/raceDistrib.png'
	
	return src
	

def racePercentSrc(df):	
	fig = (df['RaceDesc'].value_counts()[0:20].plot(kind='pie',figsize=(8,8),title='Staff Percentage Per Race',fontsize=20,autopct='%1.1f%%', label='',colormap=cmap2)).get_figure()
	img_file = 'racePercent.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/racePercent.png'
	
	return src

	
def genderCountSrc(df):	
	g = sns.countplot(df["Sex"])
	g = plt.title("Staff Gender Counts")
	img_file = 'genderCount.png'
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/genderCount.png'

	return src	
	
	
def ageCountSrc(df):	
	g = sns.catplot("Age", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Distribution of Ages Among Staff")
	img_file = 'ageCount.png'
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/ageCount.png'

	return src
		

def maritalDistribSrc(df):	
	table = pd.crosstab(index=df["Department"], columns=df["MaritalDesc"])	
	fig = (table.plot(kind="barh",figsize=(10,5),stacked=True,title='Marital Status Distribution By Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'maritalDistrib.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/maritalDistrib.png'
	
	return src


def raceDistrib2Src(df):	
	table = pd.crosstab(index=df["Department"], columns=df["RaceDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Race Distribution By Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'raceDistrib2.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/raceDistrib2.png'
	
	return src

	
def genderDistribSrc(df):
	table = pd.crosstab(index=df["Department"], columns=df["Sex"])
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=False, title='Gender Distribution By Dept')).get_figure()
	img_file = 'genderDistrib.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/genderDistrib.png'

	return src	
		
		
def rftMaritalSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["MaritalDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Marital Status').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'rftMarital.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/rftMarital.png'

	return src	


def rftRaceSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["RaceDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Race').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'rftRace.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/rftRace.png'

	return src	
	
	
def rftGenderSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["Sex"])		
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Gender').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'rftGender.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/rftGender.png'

	return src	

	
def employCosts2018Src(df):	
	fig = (df.plot(kind="barh", figsize=(10,8), stacked=True, colormap=cmap1,title='2018 Employment Source Costs').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'employCosts2018.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/employCosts2018.png'

	return src	


def raceEmploySrcSrc(df):	
	table = pd.crosstab(index=df["EmployeeSource"], columns=df["RaceDesc"])
	fig = (table.plot(kind="barh", figsize=(15,12), stacked=True, title='Pre-Hire Employee Source By Race').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'raceEmploySrc.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/raceEmploySrc.png'

	return src	
	

def genderEmploySrcSrc(df):	
	table = pd.crosstab(index=df["EmployeeSource"], columns=df["Sex"])
	fig = (table.plot(kind="barh", figsize=(15,12), stacked=True, title='Pre-Hire Employee Source By Gender').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'genderEmploySrc.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/genderEmploySrc.png'

	return src		


def perfScoreCountSrc(df):	
	ps_df = df[~df.PerformanceScore.str.startswith('Not applicable')]
	table = pd.crosstab(index=ps_df["ManagerName"], columns=ps_df["PerformanceScore"])	
	fig = (table.plot(kind="barh",figsize=(12,10),stacked=True,title='Performance Score Counts Given Per Manager').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'perfScoreCount.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/perfScoreCount.png'

	return src
	
		
def deptPerfScoreCountSrc(df):	
	ps_df = df[~df.PerformanceScore.str.startswith('Not applicable')]
	table = pd.crosstab(index=ps_df["Department"], columns=ps_df["PerformanceScore"])
	fig = (table.plot(kind="barh",figsize=(10,8),stacked=True,title='Performance Score Counts Per Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	img_file = 'deptPerfScoreCount.png'
	fig.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/deptPerfScoreCount.png'

	return src


def staffPerfScoreDistribSrc(df):	
	g = sns.factorplot("PerformanceScore", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Staff Performance Score Distribution")
	img_file = 'staffPerfScoreDistrib.png'
	plt.savefig(os.path.join(IMG_DIR, img_file), bbox_inches='tight')
	plt.clf()
	plt.close()	
	src = '../static/img/staffPerfScoreDistrib.png'

	return src	
	

	
if __name__ == '__main__':
    app.run(debug=False)
	
	
