# -*- coding: utf-8 -*-

#### IMPORTS 1.0

import os
import re
import scraperwiki
import urllib2
from datetime import datetime
from bs4 import BeautifulSoup


#### FUNCTIONS 1.2

import requests  # import requests to make sessions and post requests

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


def validateURL(url, session, datadict):
    try:
        r = session.post(url, data=datadict, allow_redirects=True, timeout=120)
        count = 1
        while r.status_code == 500 and count < 4:
            print ("Attempt {0} - Status code: {1}. Retrying.".format(count, r.status_code))
            count += 1
            r = session.post(url, data = datadict, allow_redirects=True, timeout=120)

        sourceFilename = r.headers.get('Content-Disposition')
        if sourceFilename:
            ext = os.path.splitext(sourceFilename)[1].replace('"', '').replace(';', '').replace(' ', '')
        else:
            ext = os.path.splitext(url)[1]
            ext = '.csv'
        validURL = r.status_code == 200
        validFiletype = ext.lower() in ['.csv', '.xls', '.xlsx']
        return validURL, validFiletype
    except:
        print ("Error validating URL.")
        return False, False


def validate(filename, file_url, session, datadict):
    validFilename = validateFilename(filename)
    validURL, validFiletype = validateURL(file_url, session, datadict)
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
session_url = 'http://www.torbay.gov.uk/Public_Reports/rdPage.aspx?rdReport=AP_500_Report&Mode=AnalGrid&rdAgRefreshData=True&Version=&rdRequestForwarding=Form&lbxPeriod={}&lbxYear={}&rdCSRFKey=afa57940-b000-4dbe-8744-1d09870bb8fc&rdRnd=15879&rdShowElementHistory='
errors = 0
headers = {'User-Agent': 'Mozilla/5.0'}
data = []

#### READ HTML 1.2


session = requests.Session()
pages = session.get(url, headers = headers, allow_redirects=True, verify = False)
soup = BeautifulSoup(pages.text, 'lxml')


#### SCRAPE DATA

dates = soup.find('select', id='lbxPERIOD').find_all('option')
rdcrf = soup.find('input', id='rdCSRFKey1')['value']
for date in dates:
    date = date['value']
    if 'None' not in date:
        url = 'http://www.torbay.gov.uk/Public_Reports/rdPage.aspx?rdReport=AP_500_AnalGrid_V1&rdAgRefreshData=True&lbxPERIOD={}&rdSubReport=True&rdResizeFrame=True'.format(date)
        dates_pages = session.get(url, headers = headers, allow_redirects=True, verify = False)
        dates_soup = BeautifulSoup(dates_pages.text, 'lxml')
        csv_url = 'http://www.torbay.gov.uk/Public_Reports/'+dates_soup.find('a', id='lblExportCsv_rdPopupOptionItem')['href'].split("javascript:SubmitForm('")[-1].split("','_blank'")[0].replace('%26', '&').replace('%3d', '=')
        datadict = {
            'rdCSRFKey': '{}'.format(rdcrf),
'rdAgDataColumnDetails':	',DATEYEAR;Year:Text,DATEMONTH;Month:Text,BODYNAME;Organisation:Text,BODY;Organisation Code:Text,ORGANISATIONALUNIT;Department:Text,SERVICELABEL;Service Category Label:Text,SERVICEDIVISION;Service Division Label:Text,SERVICEDIVISONCODE;Service Division Code:Text,SUPPLIERNAME;Supplier (Beneficiary):Text,SUPPLIERID;Supplier (Beneficiary) ID:Text,SUPPLIERTYPE;Supplier (Beneficiary) Type:Text,NARRATIVE;Purpose of Expenditure (Narrative):Text,EXPENDITURECATEGORY;Purpose of Expenditure (Expenditure Category):Text,SERCOPDETAILEDEXPENDITURETYPE;CIPFA Detailed Expenditure Type:Text,SERCOPDETAILEDEXPENDITURECODE;CIPFA Expenditure Code:Text,PROCATNARR;Procurement (Merchant Category):Text,PROCATCODE;Procurement (Merchant Category Code):Text,TRANSACTIONDATE;Date:Date,TRANSACTIONNUMBER;Transaction Number:Text,AMOUNT;Net Amount:Number,VATNOTRCVBL;Irrecoverable VAT:Number,GPCCARD;Card Transaction:Text,CONTRACTID;Contract ID:Text,GRANTPERIOD;Time Period for Grant:Text,GRANTREGNO;Beneficiary Registration Number:Text,GRANTPURPOSE;Purpose of Grant:Text',
'rdAgCurrentOpenPanel': '',
'rdAllowCrosstabBasedOnCurrentColumns':	'True',
'rdAgCalcName': '',
'rdAgCalcDataColumns': '',
'rdAgCalcFormula': '',
'rdAgCalcDataTypes':	'Number',
'rdAgCalcFormats': '',
'rdAgFilterColumn': '',
'rdAgFilterOperator':	'=',
'rdAgPickDistinctColumns':	',BODY,ORGANISATIONALUNIT,SERVICELABEL,SERVICEDIVISION,SERVICEDIVISONCODE,EXPENDITURECATEGORY,SERCOPDETAILEDEXPENDITURETYPE,SERCOPDETAILEDEXPENDITURECODE,',
'rdAgPickDateColumns':	',TRANSACTIONDATE,',
'rdAgCurrentFilterValue': '',
'rdAgCurrentDateType': '',
'rdAgColumnFormats':	'DATEYEAR:|DATEMONTH:|BODYNAME:|BODY:|ORGANISATIONALUNIT:|SERVICELABEL:|SERVICEDIVISION:|SERVICEDIVISONCODE:|SUPPLIERNAME:|SUPPLIERID:|SUPPLIERTYPE:|NARRATIVE:|EXPENDITURECATEGORY:|SERCOPDETAILEDEXPENDITURETYPE:|SERCOPDETAILEDEXPENDITURECODE:|PROCATNARR:|PROCATCODE:|TRANSACTIONDATE:Short Date|TRANSACTIONNUMBER:|AMOUNT:###,###,##0.00|VATNOTRCVBL:###,###,##0.00|GPCCARD:|CONTRACTID:|GRANTPERIOD:|GRANTREGNO:|GRANTPURPOSE:|',
'rdAgColumnDataTypes':	'DATEYEAR:Text|DATEMONTH:Text|BODYNAME:Text|BODY:Text|ORGANISATIONALUNIT:Text|SERVICELABEL:Text|SERVICEDIVISION:Text|SERVICEDIVISONCODE:Text|SUPPLIERNAME:Text|SUPPLIERID:Text|SUPPLIERTYPE:Text|NARRATIVE:Text|EXPENDITURECATEGORY:Text|SERCOPDETAILEDEXPENDITURETYPE:Text|SERCOPDETAILEDEXPENDITURECODE:Text|PROCATNARR:Text|PROCATCODE:Text|TRANSACTIONDATE:Date|TRANSACTIONNUMBER:Text|AMOUNT:Number|VATNOTRCVBL:Number|GPCCARD:Text|CONTRACTID:Text|GRANTPERIOD:Text|GRANTREGNO:Text|GRANTPURPOSE:Text|',
'rdAgSlidingTimeStartDateFilterOperator':	'Specific Date',
'rdAgSlidingTimeStartDateFilterOperatorOptions':	'Today',
'rdAgFilterStartDate': '',
'rdAgFilterStartDate_Hidden': '',
'rdReformatDaterdAgFilterStartDate':	'yyyy-MM-dd',
'rdDateFormatrdAgFilterStartDate':	'M/d/yyyy',
'rdAgFilterStartTime': '',
'rdAgFilterStartTime_Hidden':	'1:39 PM',
'rdReformatTimerdAgFilterStartTime':	'HH:mm:ss',
'rdFormatTimerdAgFilterStartTime':	't',
'rdAgSlidingTimeEndDateFilterOperator':	'Specific Date',
'rdAgSlidingTimeEndDateFilterOperatorOptions':	'Today',
'rdAgFilterEndDate': '',
'rdAgFilterEndDate_Hidden': '',
'rdReformatDaterdAgFilterEndDate':	'yyyy-MM-dd',
'rdDateFormatrdAgFilterEndDate':	'M/d/yyyy',
'rdAgFilterEndTime':	'',
'rdAgFilterEndTime_Hidden':	'1:39 PM',
'rdReformatTimerdAgFilterEndTime':	'HH:mm:ss',
'rdFormatTimerdAgFilterEndTime':	't',
'rdAgFilterValue': '',
'rdAgCurrentOpenTablePanel':	'Layout',
'rdAgId':	'ag500ExpenditureReportVersion2',
'rdAgReportId':	'AP_500_AnalGrid_V2',
'rdAgDraggablePanels':	'True',
'rdAgPanelOrder':	'rowTable',
'iclLayout_rdExpandedCollapsedHistory': '',
'iclLayout':	'Organisation',
'iclLayout':	'OrganisationCode',
'iclLayout':	'Department',
'iclLayout':	'ServiceCategoryLabel',
'iclLayout':	'ServiceDivisionLabel',
'iclLayout':	'ServiceDivisionCode',
'iclLayout':	'Supplier(Beneficiary)',
'iclLayout':	'Supplier(Beneficiary)ID',
'iclLayout':	'Supplier(Beneficiary)Type',
'iclLayout':	'PurposeofExpenditure(Narrative)',
'iclLayout':	'PurposeofExpenditure(ExpenditureCategory)',
'iclLayout':	'CIPFADetailedExpenditureType',
'iclLayout':	'CIPFAExpenditureCode',
'iclLayout':	'Procurement(MerchantCategory)',
'iclLayout':	'Procurement(MerchantCategoryCode)',
'iclLayout':	'Date',
'iclLayout':	'TransactionNumber',
'iclLayout':	'NetAmount',
'iclLayout':	'IrrecoverableVAT',
'iclLayout':	'CardTransaction',
'iclLayout':	'ContractID',
'iclLayout':	'TimePeriodforGrant',
'iclLayout':	'BeneficiaryRegistrationNumber',
'iclLayout':	'PurposeofGrant',
'rdAgGroupColumn':	'',
'rdAgPickDateColumnsForGrouping':	',TRANSACTIONDATE,',
'rdAgDateGroupBy':	'',
'rdAgAggrColumn':	'',
'rdAgAggrFunction':	'SUM',
'rdAgAggrRowPosition':	'RowPositionTop',
'rdAgOrderColumn':	'',
'rdAgOrderDirection':	'Ascending',
'rdAgPaging':	'ShowPaging',
'rdAgRowsPerPage':	'20',
'dtAnalysisGrid-PageNr':	'1',
'rdFix4Firefox':	'',
'rdAgCurrentOpenTablePanel':	'',
'rdShowElementHistory':	'',
'rdAgFilterValueBoolean':	'False',
'rdAgExcludeDetailRowsCheckbox':	'',
'rdRnd':	'60529',
'rdRnd':	'33072'
        }
        csvYr = date[:4]
        csvMth = date[-2:]
        csvMth = convert_mth_strings(csvMth.upper())
        data.append([csvYr, csvMth, csv_url, session, datadict])


#### STORE DATA 1.0

for row in data:
    csvYr, csvMth, url, session, datadict = row
    filename = entity_id + "_" + csvYr + "_" + csvMth
    todays_date = str(datetime.now())
    file_url = url.strip()

    valid = validate(filename, file_url, session, datadict)

    if valid == True:
        # scraperwiki.sqlite.save(unique_keys=['l'], data={"l": file_url, "f": filename, "d": todays_date })
        # print filename
        print 'scraper needs POST requests to get the spending files'
    else:
        errors += 1

if errors > 0:
    raise Exception("%d errors occurred during scrape." % errors)


#### EOF
