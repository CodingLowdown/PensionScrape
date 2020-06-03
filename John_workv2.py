#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 10:34:38 2020

@author: nicholaslowe
"""

import pandas as pd
from bs4 import BeautifulSoup as bs
import requests
import os
import openpyxl
import time
import re
os.getcwd()

os.chdir('/Users/nicholaslowe/Desktop/code/John')
BASE_DOMAIN='https://www.brightscope.com'
s=requests.session()
inputfile='/Users/nicholaslowe/Downloads/singleemployerlist pension 10000 participants.xlsx'
InputFile=pd.read_excel(inputfile,

              sheet_name='20180228'
              , converters={'Pension Plan EIN': lambda x: str(x)}) 
PensionPlanSponsorNameList=InputFile['Pension Plan Sponsor Name'].to_list()


headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }





# get the API KEY here: https://developers.google.com/custom-search/v1/overview
API_KEY = "AIzaSyCPIAqAqCl5Soj8GCbTMmQtDXi6f3zB0FM"
# get your Search Engine ID on your CSE control panel
SEARCH_ENGINE_ID = "015311924500521629147:8od8ivsatvx"
















def google_search_brightscope(s,InputFile,runnum):
    Sponsor_Name=InputFile.iloc[runnum]['Pension Plan Sponsor Name']
    Plan_Name=InputFile.iloc[runnum]['Pension Plan Name']
    EIN=str(InputFile.iloc[runnum]['Pension Plan EIN'])[:2]+'-'+ str(InputFile.iloc[runnum]['Pension Plan EIN'])[2:]
    NameSearch=InputFile.iloc[runnum]['Pension Plan Name']
    InputSearchName=NameSearch+' EIN '+EIN+' '+InputFile.iloc[runnum]['City']+' '+InputFile.iloc[runnum]['State']
   # the search query you want
    query = InputSearchName
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
    data = requests.get(url).json()
    
    

    try:
        url=data['items'][0]['link'].replace('/20'+data['items'][0]['link'].split('/20')[1],'/2018/')
    except:
        try:
            url=data['items'][0]['link']
        
        except:
            InputSearchName=NameSearch+' EIN '+EIN
            query = InputSearchName
            # constructing the URL
            # doc: https://developers.google.com/custom-search/v1/using_rest
            url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
            data = requests.get(url).json()
            try:
                url=data['items'][0]['link'].replace('/20'+data['items'][0]['link'].split('/20')[1],'/2018/')
            except:
                try:
                    url=data['items'][0]['link']
                except:
                    InputSearchName=NameSearch
                    query = InputSearchName
                    # constructing the URL
                    # doc: https://developers.google.com/custom-search/v1/using_rest
                    url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&q={query}"
                    data = requests.get(url).json()
                    try:
                        url=data['items'][0]['link'].replace('/20'+data['items'][0]['link'].split('/20')[1],'/2018/')
                    except:
                        url=data['items'][0]['link']
    return url,Plan_Name,Sponsor_Name
    


def run_all_plans(s,url):
    
    Outputdomsearch=url
    
    res=s.get(Outputdomsearch)

    return res,Outputdomsearch


def get_html_output(s,res,Outputdomsearch):

    soup=bs(res.text)
    
    outputneeded=soup.find_all('div',{"class":"grid bs-inner-section"})
    
    if not outputneeded:
        Outputdomsearch=Outputdomsearch.replace('2018','2017')
        time.sleep(5)
        res=s.get(Outputdomsearch)
        soup=bs(res.text)
        outputneeded=soup.find_all('div',{"class":"grid bs-inner-section"})
    
    return outputneeded

def create_data_tables(s,outputneeded,Plan_Name,url,Sponsor_Name):

    ColumnName=[]
    ColumnVal=[]
    for i in outputneeded:
        try:
            i.find('ul').find_all('li')
        except:
            continue
        for j in i.find('ul').find_all('li'):
            try:
                ColumnVal.append(j.find_all('span')[1].text.replace('\n',''))
                ColumnName.append(j.find_all('span')[0].text)
            except:
                continue         
    for ij in outputneeded:
        for ijk in ij.find_all('div',{"class":"module clearfix"}):
            if ijk.find('h3').text== 'Other Service Providers Receiving Direct or Indirect Compensation':
                tables=pd.read_html(str(ijk.find('table')))

    try:
        df2=pd.concat(tables)
        df = pd.DataFrame([ColumnVal],columns=ColumnName)
        df.insert(loc=0, column='Plan_Name', value=Plan_Name)
        df.insert(loc=1, column='URL', value=url)
        df.insert(loc=2, column='Sponsor_Name', value=Sponsor_Name)
        dflist=[]
        ijcount=0
        while ijcount < len(df2.columns):
            dflist.append(df2.iloc[:, ijcount].to_list())
            ijcount+=1
        
        df2.insert(loc=0, column='Plan_Name', value=Plan_Name)
        df5 = pd.merge(df,df2,how='left',left_on='Plan_Name',right_on='Plan_Name')
    except:
        df = pd.DataFrame([ColumnVal],columns=ColumnName)
        df.insert(loc=0, column='Plan_Name', value=Plan_Name)
        df.insert(loc=1, column='URL', value=url)
        df.insert(loc=2, column='Sponsor_Name', value=Sponsor_Name)
        df5=df
    file_name="/results/"+Plan_Name
    df5.to_csv(os.getcwd()+file_name+".csv")
    return df5
    
    
def master_run(s,InputFile,runnum):
    url,Plan_Name,Sponsor_Name=google_search_brightscope(s,InputFile,runnum)
    res,Outputdomsearch=run_all_plans(s,url)
    outputneeded=get_html_output(s,res,Outputdomsearch)
    Tables=create_data_tables(s,outputneeded,Plan_Name,url,Sponsor_Name)
    
    return Tables


runnum=183

while runnum<= len(PensionPlanSponsorNameList):
    try:
        master_run(s,InputFile,runnum)
    except:

        print("MISSING NUMBER "+ str(runnum))
        runnum+=1
        continue
        
    time.sleep(10)
    runnum+=1
    continue



import glob
all_files = glob.glob(os.getcwd() + "/results/*.csv")

li = []

for filename in all_files:
    companyname=filename.split('results/')[1].split('.csv')[0]
    df6 = pd.read_csv(filename, index_col=None, header=0)
    li.append(df6)


Pensionframe = pd.concat(li, axis=0, ignore_index=True)
startlen=(len(li[0].columns))
startdfnum=0
for ind,i in enumerate(li):
    if len(i.columns)>startlen:
        startdfnum=ind
        startlen=len(i.columns)
        
        
    

Pensionframe = Pensionframe[li[startdfnum].columns]
Pensionframe.to_excel("Output.xlsx",
             sheet_name='Plan Details')