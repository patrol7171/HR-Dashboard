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
from sqlalchemy import create_engine, MetaData, inspect, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Text, Float
from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, jsonify, render_template, request, redirect, url_for, make_response
import json
import urllib
import requests
import pdfkit
import datetime
from dateutil.parser import parse
from collections import defaultdict, ChainMap, OrderedDict
pd.options.mode.chained_assignment = None
import mysql.connector


from matplotlib import cm
current_palette = sns.color_palette("muted", n_colors=30)
cmap1 = cm.get_cmap('gist_rainbow')
cmap2 = cm.get_cmap('rainbow')
cs1 = cm.Dark2(np.arange(40))
cs2 = cm.Paired(np.arange(40))




#################################################
# Flask Setup
#################################################
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False




#################################################
# MySQL Config
#################################################
####### FOR HEROKU DEPLOYMENT ONLY ########:
MYSQLCONNECTION = os.environ.get('CLEARDB_DATABASE_URL')
####### FOR LOCAL USE ONLY ########:
# from config import mysql_cleardb
# MYSQLCONNECTION = mysql_cleardb





#################################################
# Database Setup
#################################################
app.config['SQLALCHEMY_DATABASE_URI'] = MYSQLCONNECTION
app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 20
db = SQLAlchemy(app)
engine = db.create_engine(MYSQLCONNECTION, pool_timeout=20, pool_recycle=299)
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
# Flask Routes
#################################################
@app.route("/")
def index():
	"""Render Home Page"""	
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	sql_stmnt2 = "Select * from recruiting_costs"
	df2 = getRecruitCostsDF(sql_stmnt2)
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]	
	allEmp_df = df.copy()
	costs_df = df2.copy()
	
	src1 = deptSrc(current_df)
	src2 = recruitingSrc(costs_df)
	src3 = staffPerfSrc(current_df)
	src4 = termReasonsSrc(allEmp_df)
		
	return render_template('index.html', src1=src1, src2=src2, src3=src3, src4=src4)
	
	
	
@app.route("/demographics")
def demographics():
	"""Render Employee Demographics Page"""
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]
	
	src1 = empStatusSrc(df)
	src2 = deptSrc(current_df)
	src3 = deptCountSrc(current_df)
	src4 = positionCountSrc(current_df)
	src5 = raceDistribSrc(current_df)
	src6 = racePercentSrc(current_df)
	src7 = genderCountSrc(current_df)
	src8 = ageCountSrc(current_df)
	src9 = maritalDistribSrc(current_df)
	src10 = raceDistrib2Src(current_df)
	src11 = genderDistribSrc(current_df)
	src12 = staffLocalesSrc(current_df)
		
	return render_template("demographics.html", src1=src1, src2=src2, src3=src3, src4=src4, src5=src5,
		src6=src6, src7=src7, src8=src8, src9=src9, src10=src10, src11=src11, src12=src12)
		
	
	
@app.route('/demographics_pdf')
def demographics_pdf():

	
	return response
		
	
	
@app.route("/recruiting")
def recruiting():
	"""Render Recruitment Page"""
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	sql_stmnt2 = "Select * from recruiting_costs"
	df2 = getRecruitCostsDF(sql_stmnt2)		
	allEmp_df = df.copy()
	costs_df = df2.copy()
	
	src1 = recruitingSrc(costs_df)
	src2 = employCosts2018Src(costs_df)
	src3 = raceEmploySrcSrc(allEmp_df)
	src4 = genderEmploySrcSrc(allEmp_df)
	
	return render_template("recruiting.html", src1=src1, src2=src2, src3=src3, src4=src4)
	
	

@app.route("/attrition")
def attrition():
	"""Render Employee & Site Locater Page"""
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	allEmp_df = df.copy()	
	
	src1 = termReasonsSrc(allEmp_df)
	src2 = rftRaceSrc(allEmp_df)
	src3 = rftMaritalSrc(allEmp_df)
	src4 = rftGenderSrc(allEmp_df)
	
	return render_template("attrition.html", src1=src1, src2=src2, src3=src3, src4=src4)

	
	
@app.route("/talent")
def talent():
	"""Render HR Policies & Rules Page"""
	sql_stmnt = "Select * from employee_data"
	df = getDataDF(sql_stmnt)
	current_df = df[~df['EmploymentStatus'].str.contains('Terminated for Cause|Voluntarily Terminated')]	
	allEmp_df = df.copy()	
	
	src1 = staffPerfSrc(current_df)
	src2 = staffPerfScoreDistribSrc(current_df)
	src3 = perfScoreCountSrc(allEmp_df)
	src4 = deptPerfScoreCountSrc(allEmp_df)
		
	return render_template("talent.html", src1=src1, src2=src2, src3=src3, src4=src4)

	
	
@app.route("/glossary")
def glossary():
	"""Render HR Policies & Rules Page"""
	
	return render_template("glossary.html")	
	

	
	
#################################################
# App Functions
#################################################
def getDataDF(sql):	
	df = pd.read_sql_query(sql, db.session.bind)	
	
	return df	
	
	
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
	fig.savefig('static/img/dept.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/dept.png'
	
	return src	
		

def recruitingSrc(df):	
	totalsTbl2018 = df.sum(axis=1)
	top10_2018costs = totalsTbl2018.nlargest(10)
	fig = (top10_2018costs.plot(kind='pie',figsize=(8,8),autopct='%1.1f%%',colormap=cmap2,title='2018 Top 10 Costliest Employment Sources',
		label='',fontsize=20)).get_figure()
	fig.savefig('static/img/top10recruit.png', bbox_inches='tight')	
	plt.clf()	
	src = '../static/img/top10recruit.png'
	
	return src	


def staffPerfSrc(df):	
	fig = (df['PerformanceScore'].value_counts()[0:20].plot(kind='pie',figsize=(8,8),autopct='%1.1f%%',colormap=cmap2,
		title='Current Staff Performance Score Results',label='',fontsize=20)).get_figure()
	fig.savefig('static/img/staffPerf.png', bbox_inches='tight')	
	plt.clf()
	plt.close()	
	src = '../static/img/staffPerf.png'
	
	return src
		
	
def termReasonsSrc(df):	   
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	fig5 =(rft_df['ReasonForTerm'].value_counts()[0:20].plot(kind='barh',figsize=(10,8),colormap=cmap1,title='Reasons For Termination')).get_figure()
	fig5.savefig('static/img/termReasons.png', bbox_inches='tight')	
	plt.clf()
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
	plt.savefig('static/img/staffLocale.png', bbox_inches='tight')
	plt.clf()
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
	plt.savefig('static/img/status.png', bbox_inches='tight')
	plt.clf()
	src = '../static/img/status.png'
	
	return src	

	
def deptCountSrc(df):		
	fig = (df['Department'].value_counts()[0:20].plot(kind='barh',figsize=(10,8),title='Current Staff Count Per Dept',label='',fontsize=20)).get_figure()
	fig.savefig('static/img/deptCount.png', bbox_inches='tight')	
	plt.clf()
	src = '../static/img/deptCount.png'
	
	return src
	
	
def positionCountSrc(df):	
	plt.figure(figsize=(16,8))
	sns.countplot('Position', data=df)
	plt.xticks(rotation = 60, ha='right')
	plt.title('Current Staff Count Per Position')
	plt.tight_layout()
	plt.savefig('static/img/positionCount.png', bbox_inches='tight')
	plt.clf()
	src = '../static/img/positionCount.png'

	return src
		

def raceDistribSrc(df):	
	g = sns.catplot("RaceDesc", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Staff Racial Distribution")
	plt.savefig('static/img/raceDistrib.png', bbox_inches='tight')
	plt.clf()
	src = '../static/img/raceDistrib.png'
	
	return src
	

def racePercentSrc(df):	
	fig = (df['RaceDesc'].value_counts()[0:20].plot(kind='pie',figsize=(8,8),title='Staff Percentage Per Race',autopct='%1.1f%%', label='',colormap=cmap2)).get_figure()
	fig.savefig('static/img/racePercent.png', bbox_inches='tight')
	plt.clf()
	src = '../static/img/racePercent.png'
	
	return src

	
def genderCountSrc(df):	
	g = sns.countplot(df["Sex"])
	g = plt.title("Staff Gender Counts")
	plt.savefig('static/img/genderCount.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/genderCount.png'

	return src	
	
	
def ageCountSrc(df):	
	g = sns.catplot("Age", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Distribution of Ages Among Staff")
	plt.savefig('static/img/ageCount.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/ageCount.png'

	return src
		

def maritalDistribSrc(df):	
	table = pd.crosstab(index=df["Department"], columns=df["MaritalDesc"])	
	fig = (table.plot(kind="barh",figsize=(10,5),stacked=True,title='Marital Status Distribution By Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/maritalDistrib.png', bbox_inches='tight')
	plt.clf()
	src = '../static/img/maritalDistrib.png'
	
	return src


def raceDistrib2Src(df):	
	table = pd.crosstab(index=df["Department"], columns=df["RaceDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Race Distribution By Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/raceDistrib2.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/raceDistrib2.png'
	
	return src

	
def genderDistribSrc(df):
	table = pd.crosstab(index=df["Department"], columns=df["Sex"])
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=False, title='Gender Distribution By Dept')).get_figure()
	fig.savefig('static/img/genderDistrib.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/genderDistrib.png'

	return src	
		
		
def rftMaritalSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["MaritalDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Marital Status').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/rftMarital.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/rftMarital.png'

	return src	


def rftRaceSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["RaceDesc"])	
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Race').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/rftRace.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/rftRace.png'

	return src	
	
	
def rftGenderSrc(df):
	rft_df = (df[~df.ReasonForTerm.str.startswith('Not applicable')]).copy()
	table = pd.crosstab(index=rft_df["ReasonForTerm"], columns=rft_df["Sex"])		
	fig = (table.plot(kind="barh", figsize=(10,5), stacked=True, title='Reason For Term By Gender').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/rftGender.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/rftGender.png'

	return src	

	
def employCosts2018Src(df):	
	fig = (df.plot(kind="barh", figsize=(10,8), stacked=True, colormap=cmap1,title='2018 Employment Source Costs').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/employCosts2018.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/employCosts2018.png'

	return src	


def raceEmploySrcSrc(df):	
	table = pd.crosstab(index=df["EmployeeSource"], columns=df["RaceDesc"])
	fig = (table.plot(kind="barh", figsize=(15,12), stacked=True, title='Pre-Hire Employee Source By Race').legend(bbox_to_anchor=(1,1))	).get_figure()
	fig.savefig('static/img/raceEmploySrc.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/raceEmploySrc.png'

	return src	
	

def genderEmploySrcSrc(df):	
	table = pd.crosstab(index=df["EmployeeSource"], columns=df["Sex"])
	fig = (table.plot(kind="barh", figsize=(15,12), stacked=True, title='Pre-Hire Employee Source By Gender').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/genderEmploySrc.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/genderEmploySrc.png'

	return src		


def perfScoreCountSrc(df):	
	ps_df = df[~df.PerformanceScore.str.startswith('Not applicable')]
	table = pd.crosstab(index=ps_df["ManagerName"], columns=ps_df["PerformanceScore"])	
	fig = (table.plot(kind="barh",figsize=(12,10),stacked=True,title='Performance Score Counts Given Per Manager').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/perfScoreCount.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/perfScoreCount.png'

	return src
	
		
def deptPerfScoreCountSrc(df):	
	ps_df = df[~df.PerformanceScore.str.startswith('Not applicable')]
	table = pd.crosstab(index=ps_df["Department"], columns=ps_df["PerformanceScore"])
	fig = (table.plot(kind="barh",figsize=(10,8),stacked=True,title='Performance Score Counts Per Dept').legend(bbox_to_anchor=(1,1))).get_figure()
	fig.savefig('static/img/deptPerfScoreCount.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/deptPerfScoreCount.png'

	return src


def staffPerfScoreDistribSrc(df):	
	g = sns.factorplot("PerformanceScore", data=df, aspect=4, kind="count")
	g.set_xticklabels(rotation=0)
	g = plt.title("Staff Performance Score Distribution")
	plt.savefig('static/img/staffPerfScoreDistrib.png', bbox_inches='tight')
	plt.clf()	
	src = '../static/img/staffPerfScoreDistrib.png'

	return src	
	
	
	
	
if __name__ == '__main__':
    app.run(debug=True,threaded=True)
	
	
