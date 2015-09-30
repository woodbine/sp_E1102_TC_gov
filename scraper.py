# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from dateutil.parser import parse

#### FUNCTIONS 1.0

def validateFilename(filename):
    filenameregex = '^[a-zA-Z0-9]+_[a-zA-Z0-9]+_[a-zA-Z0-9]+_[0-9][0-9][0-9][0-9]_[0-9QY][0-9]$'
    dateregex = '[0-9][0-9][0-9][0-9]_[0-9QY][0-9]'
    validName = (re.search(filenameregex, filename) != None)
    found = re.search(dateregex, filename)
    if not found:
        return False
    date = found.group(0)
    now = datetime.now()
    year, month = date[:4], date[5:7]
    validYear = (2000 <= int(year) <= now.year)
    if 'Q' in date:
        validMonth = (month in ['Q0', 'Q1', 'Q2', 'Q3', 'Q4'])
    elif 'Y' in date:
        validMonth = (month in ['Y1'])
    else:
        try:
            validMonth = datetime.strptime(date, "%Y_%m") < now
        except:
            return False
    if all([validName, validYear, validMonth]):
        return True


def validateURL(url):
    try:
        r = requests.get(url, allow_redirects=True, timeout=20)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = requests.get(url, allow_redirects=True, timeout=20)
        sourceFilename = r.headers.get('Content-Disposition')

        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        if r.headers.get('Content-Type') == 'application/octet-stream':
            ext = '.csv'
        else:
            ext = os.path.splitext(url)[1]
        validURL = r.status_code == 200
        validFiletype = ext in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False

def validate(filename, file_url):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url)
    if not validFilename:
        print filename, "*Error: Invalid filename*"
        print file_url
        return False
    if not validURL:
        print filename, "*Error: Invalid URL*"
        print file_url
        return False
    if not validFiletype:
        print filename, "*Error: Invalid filetype*"
        print file_url
        return False
    return True


def convert_mth_strings ( mth_string ):
    month_numbers = {'JAN': '01', 'FEB': '02', 'MAR':'03', 'APR':'04', 'MAY':'05', 'JUN':'06', 'JUL':'07', 'AUG':'08', 'SEP':'09','OCT':'10','NOV':'11','DEC':'12' }
    for k, v in month_numbers.items():
        mth_string = mth_string.replace(k, v)
    return mth_string


#### VARIABLES 1.0

entity_id = "E1102_TC_gov"
url = "http://www.torbay.gov.uk/Public_Reports/rdPage.aspx?rdReport=AP_500_Report"
errors = 0
headers = {'User-Agent': 'Mozilla/5.0'}
data = []

#### READ HTML 1.0

session = requests.Session()
pages = session.get(url, headers = headers, allow_redirects=True, verify = False)
soup = BeautifulSoup(pages.text, 'lxml')


#### SCRAPE DATA


dates = soup.find('option', attrs={'selected':'True'}).text
month = soup.find('select', attrs={'id':'lbxPeriod'}).find('option', attrs = {'selected':'True'}).text
if len(month) == 1:
    csvMth = '0'+ month
csvYr = dates

iframe  = soup.find('span', 'ThemeTextSmall').iframe['data-hiddensource']
url_csv = 'http://www.torbay.gov.uk/Public_Reports/' + iframe
pages_csv = session.get(url_csv, headers = headers, allow_redirects=True, verify = False)
soup_csv = BeautifulSoup(pages_csv.text, 'lxml')
keys = soup_csv.find('input', attrs = {'name':'rdCSRFKey'})['value']
url_link = soup_csv.find('a', attrs={'id':'actExportCSV'})['href'].split("javascript:SubmitForm('")[-1].split("','_blank'")[0]

datadict = {'rdCSRFKey':'{}'.format(keys),
'rdAgCurrentOpenPanel':''	,
'rdAllowCrosstabBasedOnCurrentColumns':'True',
'rdAgCalcName'	: '',
'rdAgCalcDataColumns'	:'',
'rdAgCalcFormula':''	,
'rdAgCalcDataTypes':'Number',
'rdAgCalcFormats':''	,
'rdAgFilterColumn':''	,
'rdAgFilterOperator':	'=',
'rdAgPickDistinctColumns':',BODY,ORGANISATIONALUNIT,SERVICELABEL,SERVICEDIVISION,SERVICEDIVISONCODE,EXPENDITURECATEGORY,SERCOPDETAILEDEXPENDITURETYPE,SERCOPDETAILEDEXPENDITURECODE,',
'rdAgPickDateColumns':	',TRANSACTIONDATE-NoCalendar,',
'rdAgCurrentFilterValue':''	,
'rdAgCurrentDateType'	: '',
'rdAgSlidingTimeStartDateFilterOpearator':'Specific Date',
'rdAgSlidingTimeStartDateFilterOpearatorOptions':'Today',
'rdAgFilterStartDate'	:'',
'rdAgFilterStartDate_Hidden':''	,
'rdReformatDaterdAgFilterStartDate':'yyyy/MM/dd',
'rdDateFormatrdAgFilterStartDate':'M/d/yyyy',
'rdAgFilterStartDateTextbox':''	,
'rdAgFilterStartDateTextbox_Hidden':''	,
'rdReformatDaterdAgFilterStartDateTextbox':'yyyy/MM/dd',
'rdDateFormatrdAgFilterStartDateTextbox':'M/d/yyyy',
'rdAgSlidingTimeEndDateFilterOpearator':'Specific Date',
'rdAgSlidingTimeEndDateFilterOpearatorOptions':'Today',
'rdAgFilterEndDate':''	,
'rdAgFilterEndDate_Hidden':''	,
'rdReformatDaterdAgFilterEndDate':'yyyy/MM/dd',
'rdDateFormatrdAgFilterEndDate':'M/d/yyyy',
'rdAgFilterEndDateTextbox':'',
'rdAgFilterEndDateTextbox_Hidden':''	,
'rdReformatDaterdAgFilterEndDateTextbox':'yyyy/MM/dd',
'rdDateFormatrdAgFilterEndDateTextbox':'M/d/yyyy',
'rdAgFilterValue':'',
'rdAgCurrentOpenTablePanel':'Layout',
'rdAgId':'ag500ExpenditureReportVersion2',
'rdAgReportId':'AP_500_AnalGrid_V2',
'rdAgDraggablePanels':'True',
'rdAgPanelOrder':'rowTable',
'rdAgLayoutColumnName_Row1':'Year',
'rdAgLayoutColumnName_Row2':'Month',
'rdAgColVisible_Row3':'True',
'rdAgLayoutColumnName_Row3':'Organisation',
'rdAgColVisible_Row4':'True',
'rdAgLayoutColumnName_Row4':'OrganisationCode',
'rdAgColVisible_Row5':'True',
'rdAgLayoutColumnName_Row5':'Department',
'rdAgColVisible_Row6':'True',
'rdAgLayoutColumnName_Row6':'ServiceCategoryLabel',
'rdAgColVisible_Row7':	'True',
'rdAgLayoutColumnName_Row7':	'ServiceDivisionLabel',
'rdAgColVisible_Row8':	'True',
'rdAgLayoutColumnName_Row8':	'ServiceDivisionCode',
'rdAgColVisible_Row9':	'True',
'rdAgLayoutColumnName_Row9':	'Supplier(Beneficiary)',
'rdAgColVisible_Row10':	'True',
'rdAgLayoutColumnName_Row10':	'Supplier(Beneficiary)ID',
'rdAgColVisible_Row11':	'True',
'rdAgLayoutColumnName_Row11':	'Supplier(Beneficiary)Type',
'rdAgColVisible_Row12':	'True',
'rdAgLayoutColumnName_Row12':	'PurposeofExpenditure(Narrative)',
'rdAgColVisible_Row13':	'True',
'rdAgLayoutColumnName_Row13':	'PurposeofExpenditure(ExpenditureCategory)',
'rdAgColVisible_Row14':	'True',
'rdAgLayoutColumnName_Row14':	'CIPFADetailedExpenditureType',
'rdAgColVisible_Row15':	'True',
'rdAgLayoutColumnName_Row15':	'CIPFAExpenditureCode',
'rdAgColVisible_Row16':	'True',
'rdAgLayoutColumnName_Row16':	'Procurement(MerchantCategory)',
'rdAgColVisible_Row17':	'True',
'rdAgLayoutColumnName_Row17':	'Procurement(MerchantCategoryCode)',
'rdAgColVisible_Row18':	'True',
'rdAgLayoutColumnName_Row18':	'Date',
'rdAgColVisible_Row19':	'True',
'rdAgLayoutColumnName_Row19':	'TransactionNumber',
'rdAgColVisible_Row20':	'True',
'rdAgLayoutColumnName_Row20':	'NetAmount',
'rdAgColVisible_Row21':	'True',
'rdAgLayoutColumnName_Row21':	'IrrecoverableVAT',
'rdAgColVisible_Row22':	'True',
'rdAgLayoutColumnName_Row22':	'CardTransaction',
'rdAgColVisible_Row23':	'True',
'rdAgLayoutColumnName_Row23':	'ContractID',
'rdAgColVisible_Row24':	'True',
'rdAgLayoutColumnName_Row24':	'TimePeriodforGrant',
'rdAgColVisible_Row25':	'True',
'rdAgLayoutColumnName_Row25':	'BeneficiaryRegistrationNumber',
'rdAgColVisible_Row26':	'True',
'rdAgLayoutColumnName_Row26':	'PurposeofGrant',
'rdAgGroupColumn':	'',
'rdAgPickDateColumnsForGrouping':	',TRANSACTIONDATE,',
'rdAgDateGroupBy':''	,
'rdAgAggrColumn':'',
'rdAgAggrFunction':	'SUM',
'rdAgAggrRowPosition':'RowPositionTop',
'rdAgOrderColumn':''	,
'rdAgOrderDirection':	'Ascending',
'rdAgPaging':	'ShowPaging',
'rdAgRowsPerPage':	'20',
'dtAnalysisGrid-PageNr':'1',
'rdFix4Firefox'	:'',
'rdAgCurrentOpenTablePanel':''	,
'rdShowElementHistory'	:'',
'rdRnd':	'17475'}
url = 'http://www.torbay.gov.uk/Public_Reports/'+url_link
p = session.post(url, headers = headers, data =datadict,  allow_redirects=True, verify =False)


csvMth = convert_mth_strings(csvMth.upper())
data.append([csvYr, csvMth, url])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url)

    if valid == True:
        scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        print filename
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF

