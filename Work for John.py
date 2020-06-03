#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:24:21 2020

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

              sheet_name='20180228') 
PensionPlanSponsorNameList=InputFile['Pension Plan Sponsor Name'].to_list()

def google_search_brightscope(s,InputFile,runnum):
    test=InputFile.iloc[runnum]['Pension Plan Sponsor Name']
    if InputFile.iloc[runnum]['Pension Plan Sponsor Name'].split(' ')[0].lower()=="the":
        InputSearchName=InputFile.iloc[runnum]['Pension Plan Sponsor Name'].split(' ')[1]+'+'+InputFile.iloc[runnum]['City']+'+'+InputFile.iloc[runnum]['State']
    else:
        InputSearchName=InputFile.iloc[runnum]['Pension Plan Sponsor Name'].split(' ')[0]+'+'+InputFile.iloc[runnum]['City']+'+'+InputFile.iloc[runnum]['State']
    
    res3=s.get('https://www.google.com/search?biw=1200&bih=920&ei=LT2zXsOAFOKrytMP_aWskAM&q=site%3Abrightscope.com+%22%22+'+InputSearchName+'+%22%22&oq=site%3Abrightscope.com+%22%22+'+InputSearchName+'+%22%22&gs_lcp=CgZwc3ktYWIQAzoECAAQR1CppQJYqaUCYLuoAmgAcAN4AIABMogBMpIBATGYAQCgAQKgAQGqAQdnd3Mtd2l6&sclient=psy-ab&ved=0ahUKEwiDy_PBp6DpAhXilXIEHf0SCzIQ4dUDCAw&uact=5')
    
    soup1 = bs(res3.text.encode('utf8'), 'html.parser')
    try:
        
        url=soup1.find("a", href=re.compile("401k-rating"))["href"].split('url?q=')[1].split('&sa')[0]
        res=s.get(url)
        soup1=bs(res.text)
        href_list=[]
        href_list_name=[]
        #href_list=[soup.find('ul',{'class','company-list-left'}).find('a')['href'].replace('401k-rating/','form-5500/basic-info/')+'2018/']
        for hrefcount in soup1.find('div',{"class":"dropdown dropdown-with-border"}).find('ul').find_all('li'):
            href_list.append(hrefcount.find('a')['href'].replace('401k-rating/','form-5500/basic-info/'))
            href_list_name.append(hrefcount.find('a').text)
        #Outputdomsearch=url.replace('401k-rating/','form-5500/basic-info/')+'2018/'
    except:
        url=soup1.find("a", href=re.compile("5500"))["href"].split('url?q=')[1].split('&sa')[0]
        url=url.replace('2017/','2018/')
        url=url.replace('2016/','2018/')
        url=url.replace('2015/','2018/')
        url=url.replace('2014/','2018/')
        url=url.replace('2013/','2018/')
        url=url.replace('2012/','2018/')
        res=s.get(url)
        soup1=bs(res.text)
        href_list=[url.split('https://www.brightscope.com')[1]]
        href_list_name=[url.split('/2018/')[0].split('/')[-1]]
    return href_list,href_list_name,test
    

def get_inital_data(s,BASE_DOMAIN,PensionPlanSponsorNameList,runnum):

    test=PensionPlanSponsorNameList[runnum]
    inputName=test.replace(' ','+')
    
    res1=s.get('https://www.brightscope.com/ratings/?company_name='+inputName+'&search_type=company')
    soup=bs(res1.text)
    res=s.get(BASE_DOMAIN+soup.find('ul',{'class','company-list-left'}).find('a')['href'])
    soup1=bs(res.text)
    href_list=[]
    href_list_name=[]
    #href_list=[soup.find('ul',{'class','company-list-left'}).find('a')['href'].replace('401k-rating/','form-5500/basic-info/')+'2018/']
    for hrefcount in soup1.find('div',{"class":"dropdown dropdown-with-border"}).find('ul').find_all('li'):
        href_list.append(hrefcount.find('a')['href'].replace('401k-rating/','form-5500/basic-info/'))
        href_list_name.append(hrefcount.find('a').text)
        
    return href_list,href_list_name,test

#res=s.get('https://www.brightscope.com/form-5500/basic-info/410548/Bank-Of-The-West/15847902/Bank-Of-The-West-401k-Savings-Plan/2018/')


def run_all_plans(s,BASE_DOMAIN,href_list_single,href_list_name_single,test):
    
    Outputdomsearch=BASE_DOMAIN+href_list_single
    
    res=s.get(Outputdomsearch)

    return res,Outputdomsearch


def get_html_output(s,res,BASE_DOMAIN,Outputdomsearch):

    soup=bs(res.text)
    
    outputneeded=soup.find_all('div',{"class":"grid bs-inner-section"})
    
    if not outputneeded:
        Outputdomsearch=Outputdomsearch.replace('2018','2017')
        time.sleep(5)
        res=s.get(BASE_DOMAIN+Outputdomsearch)
        soup=bs(res.text)
        outputneeded=soup.find_all('div',{"class":"grid bs-inner-section"})
    
    return outputneeded

def create_data_tables(s,outputneeded,test,href_list_single,href_list_name_single):

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
        df.insert(loc=0, column='FileCompName', value=test)
        df.insert(loc=1, column='URL', value=href_list_single)
        df.insert(loc=2, column='Plan Name', value=href_list_name_single)
        dflist=[]
        ijcount=0
        while ijcount < len(df2.columns):
            dflist.append(df2.iloc[:, ijcount].to_list())
            ijcount+=1
        
        df2.insert(loc=0, column='FileCompName', value=test)
        df5 = pd.merge(df,df2,how='left',left_on='FileCompName',right_on='FileCompName')
    except:
        df = pd.DataFrame([ColumnVal],columns=ColumnName)
        df.insert(loc=0, column='FileCompName', value=test)
        df.insert(loc=1, column='URL', value=href_list_single)
        df.insert(loc=2, column='Plan Name', value=href_list_name_single)
        df5=df
    file_name="/results/"+test+href_list_name_single
    df5.to_csv(os.getcwd()+file_name+".csv")
    return df5
    
    
def master_run(s,BASE_DOMAIN,PensionPlanSponsorNameList,runnum):
    outputslist=get_inital_data(s,BASE_DOMAIN,PensionPlanSponsorNameList,runnum)
    href_list=outputslist[0]
    href_list_name=outputslist[1]
    test=outputslist[2]
    for ind,runcheckcount in enumerate(href_list):
        href_list_single=href_list[ind]
        href_list_name_single=href_list_name[ind]
        outputslistrun=run_all_plans(s,BASE_DOMAIN,href_list_single,href_list_name_single,test)
        res=outputslistrun[0]
        Outputdomsearch=outputslistrun[1]
        outputneeded=get_html_output(s,res,BASE_DOMAIN,Outputdomsearch)
        Tables=create_data_tables(s,outputneeded,test,href_list_single,href_list_name_single)
    return Tables

def master_run2(s,BASE_DOMAIN,InputFile,runnum):
    outputslist=google_search_brightscope(s,InputFile,runnum)
    href_list=outputslist[0]
    href_list_name=outputslist[1]
    test=outputslist[2]
    for ind,runcheckcount in enumerate(href_list):
        href_list_single=href_list[ind]
        href_list_name_single=href_list_name[ind]
        outputslistrun=run_all_plans(s,BASE_DOMAIN,href_list_single,href_list_name_single,test)
        res=outputslistrun[0]
        Outputdomsearch=outputslistrun[1]
        outputneeded=get_html_output(s,res,BASE_DOMAIN,Outputdomsearch)
        Tables=create_data_tables(s,outputneeded,test,href_list_name_single,href_list_name_single)
    return Tables

runnum=8

while runnum<= len(PensionPlanSponsorNameList):
    try:
        master_run(s,BASE_DOMAIN,PensionPlanSponsorNameList,runnum)
    except:
        try:
            master_run2(s,BASE_DOMAIN,InputFile,runnum)
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

Pensionframe = Pensionframe[li[2].columns]
Pensionframe.to_excel("Output.xlsx",
             sheet_name='Plan Details')






df2=pd.concat(tables[4])



df = pd.DataFrame([ColumnVal],columns=ColumnName)


dflist=[df2.iloc[:, 0].to_list(),
df2.iloc[:, 1].to_list(),
df2.iloc[:, 2].to_list(),
df2.iloc[:, 3].to_list(),
df2.iloc[:, 4].to_list(),
df2.iloc[:, 5].to_list()]

df3 = pd.DataFrame({
    df2.columns.to_list()[0] : [dflist[0]],
     df2.columns.to_list()[1] : [dflist[1]],
      df2.columns.to_list()[2] : [dflist[2]],
       df2.columns.to_list()[3] : [dflist[3]],
        df2.columns.to_list()[4] : [dflist[4]],
         df2.columns.to_list()[5] : [dflist[5]]
                    
                    })




##df4=pd.merge(df, df3, left_index=True, right_index=True)
##os.getcwd()
##df4.to_csv(os.getcwd()+file_name+".csv")


df5 = pd.merge(df,df31,how='left',left_on='FileCompName',right_on='FileCompName')


writer = pd.ExcelWriter('Output.xlsx', engine='openpyxl')

df4.to_excel(writer, startrow=len(df4)+1, index=False)

writer.save()

df4.to_excel("Output",
             sheet_name='Plan Details')





##df.to_csv('401k_PLan_test_output.csv')

df.to_excel(file_name,
             sheet_name='Plan Details')
writer = pd.ExcelWriter(file_name, engine='openpyxl')

if os.path.exists(file_name):
    book = openpyxl.load_workbook(file_name)
    writer.book = book
    
df2.to_excel(writer,
             sheet_name='Service Provider')  
writer.save()
writer.close()