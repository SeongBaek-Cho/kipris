from bs4 import BeautifulSoup
import requests
import mysql.connector

def getStringvalue (item, attr) :
    try :
        value = item.find(attr).string.strip()
        if (len(value) < 1 ) :
            return None
        else :
            return value.replace("'","\'")
    except Exception as ex :
        return None

def getDateFormat (value) :
    date = value.replace("(","").replace(")","")
    return date


base = 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getWordSearch?word=염기서열&pageNo=2&ServiceKey=%s' % key
# url = 'http://plus.kipris.or.kr/openapi/rest/patUtiModInfoSearchSevice/freeSearchInfo?word=염기서열&patent=false&utility=true&docsStart=1&docsCount=50&lastvalue=R&accessKey=%s' % key
res = requests.get(base)
soup = BeautifulSoup(res.text, 'html.parser')
total_count = soup.find('count').totalcount.string
rows = 10
rest = int(total_count)%rows
print(rest)
if (rest != 0) :
    page_count = int(int(total_count)/rows)+1
    print("have rest")
    print(page_count)
else :
    page_count = int(int(total_count)/rows)
    print("not have rest")
    print(page_count)

index = 1
applicationnumber_arr = []
for x in range(page_count) :
    url = 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getWordSearch?word=염기서열&pageNo=%s&ServiceKey=%s' % (str(index), key)
    # print(index)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.findAll('item')
    for item in items :

        applicationnumber = getStringvalue(item, 'applicationnumber')
        applicationnumber_arr.append(applicationnumber)
    index +=1
    if (index == 30) :
        break


applicationnumber_arr = list(set(applicationnumber_arr))
print(applicationnumber_arr)

index=1
for number in applicationnumber_arr :
    if(index == 200 ) :
        break


    lastupdate_date = None
    create_user_id = 1

    kipridb = mysql.connector.connect(
        user='refdb',
        port=3306,
        password='ckarhansgjs',
        host='192.168.8.217',
        database='REFDB'
    )
    mycursor = kipridb.cursor()

    url = 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch?applicationNumber=%s&ServiceKey=%s' %(number, key)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    item = soup.find('item')

    # KiprisBiblioInfo
    bibliosummary = item.find('bibliosummaryinfo')
    application_date = getStringvalue(bibliosummary, 'applicationdate')
    application_number = getStringvalue(bibliosummary, 'applicationnumber')
    claim_count = getStringvalue(bibliosummary, 'claimcount')
    final_disposal = getStringvalue(bibliosummary, 'finaldisposal')
    invention_title = getStringvalue(bibliosummary, 'inventiontitle')
    invention_title_eng = getStringvalue(bibliosummary, 'inventiontitleeng')
    open_date = getStringvalue(bibliosummary, 'opendate')
    open_number = getStringvalue(bibliosummary,'opennumber')
    original_application_date = getStringvalue(bibliosummary, 'originalapplicationdate')
    original_application_kind = getStringvalue(bibliosummary, 'originalapplicationkind')
    original_application_number = getStringvalue(bibliosummary, 'originalapplicationnumber')
    original_examination_request_flag = getStringvalue(bibliosummary, 'originalexaminationrequestflag')
    original_examination_request_date = getStringvalue(bibliosummary, 'originalexaminationrequestdate')
    publication_number = getStringvalue(bibliosummary, 'publicationnumber')
    publication_date = getStringvalue(bibliosummary, 'publicationdate')
    register_date = getStringvalue(bibliosummary, 'registerdate')
    register_number = getStringvalue(bibliosummary, 'registernumber')
    register_status = getStringvalue(bibliosummary, 'registerstatus')
    application_flag = getStringvalue(bibliosummary, 'applicationflag')
    translation_submit_date = getStringvalue(bibliosummary, 'translationsubmitdate')

    fabstract = soup.find('abstractinfo')
    abstract = getStringvalue(fabstract, 'astrtcont')

    finternational = soup.find('internationalinfo')
    international_application_number = getStringvalue(finternational, 'internationalapplicationinfo')
    international_application_date = getStringvalue(finternational, 'internationalapplicationdate')
    international_open_number = getStringvalue(finternational, 'internationalopennumber')
    international_open_date = getStringvalue(finternational, 'internationalopendate')

    claim = ""
    claims = soup.findAll('claiminfo')
    for fclaim in claims :
        if (getStringvalue(fclaim, 'claim') == None ) :
            continue
        claim += getStringvalue(fclaim, 'claim')


    bsql = """INSERT INTO KiprisBiblioInfo (INVENTION_TITLE, INVENTION_TITLE_ENG, ABSTRACT, APPLICATION_NUMBER, APPLICATION_DATE, OPEN_NUMBER, 
    OPEN_DATE, PUBLICATION_NUMBER, PUBLICATION_DATE, REGISTER_NUMBER, REGISTER_DATE, ORIGINAL_APPLICATION_KIND, ORIGINAL_APPLICATION_NUMBER, 
    ORIGINAL_APPLICATION_DATE, FINAL_DISPOSAL, REGISTER_STATUS, ORIGINAL_EXAMINATION_REQUEST_FLAG, ORIGINAL_EXAMINATION_REQUEST_DATE, CLAIM,
    CLAIM_COUNT, APPLICATION_FLAG, INTERNATIONAL_APPLICATION_NUMBER, INTERNATIONAL_APPLICATION_DATE, INTERNATIONAL_OPEN_NUMBER, INTERNATIONAL_OPEN_DATE,
    TRANSLATION_SUBMIT_DATE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID ) VALUES (%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now(), %s, %s) """
    bval = (invention_title, invention_title_eng, abstract, number, application_date, open_number, open_date, publication_number, publication_date, register_number, register_date, original_application_kind, original_application_number, original_application_date, final_disposal, register_status, original_examination_request_flag, original_examination_request_date, claim, claim_count, application_flag, international_application_number, international_application_date, international_open_number, international_open_date, translation_submit_date,  lastupdate_date, create_user_id)
    print(bsql ,bval)
    mycursor.execute(bsql, bval)

    try:
        blsql = """SELECT MAX(BIBLIO_ID) FROM KiprisBiblioInfo"""
        mycursor.execute(blsql)
        biblio = mycursor.fetchone()[0]
    except:
        biblio = 0

    #KiprisIpcInfo
    ipcs = soup.findAll('ipcinfo')
    for ipc in ipcs :
        ipc_date = getDateFormat(getStringvalue(ipc, 'ipcdate'))
        ipc_number = getStringvalue(ipc, 'ipcnumber')
        if (ipc_number == None) :
            continue


        lsql = """INSERT INTO KiprisIpcInfo (IPC_NUMBER, IPC_DATE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        lval = (ipc_number, ipc_date,  lastupdate_date, create_user_id)
        mycursor.execute(lsql, lval)

        try:
            ipsql = """SELECT MAX(IPC_ID) FROM KiprisIpcInfo"""
            mycursor.execute(ipsql)
            lpcio = mycursor.fetchone()[0]
        except:
            lpcio = 0

        bisql = """INSERT INTO KiprisBiblioIpcInfo (BIBLIO_ID, IPC_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        bival = (biblio, lpcio,  lastupdate_date, create_user_id)
        mycursor.execute(bisql, bival)


    #kiprisFamilyInfo
    families = soup.findAll('familyinfo')
    for family in families :
        family_application_number = getStringvalue(family, 'familyapplicationnumber')
        if (family_application_number == None) :
            continue
        fsql = """INSERT INTO KiprisFamilyInfo (APPLICATION_NUMBER, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, now(), %s, %s)"""
        fval = (family_application_number,  lastupdate_date, create_user_id)
        mycursor.execute(fsql, fval)

        try:
            fasql = """SELECT MAX(FAMILY_ID) FROM KiprisFamilyInfo"""
            #faval = (family_application_number) #확인
            mycursor.execute(fasql)
            faio = mycursor.fetchone()[0]
        except:
            faio = 0

        faisql = """INSERT INTO KiprisBiblioFamilyInfo (BIBLIO_ID, FAMILY_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        faival = (biblio, faio,  lastupdate_date, create_user_id)
        mycursor.execute(faisql, faival)

    #KiprisPersonInfo
    inventors = soup.findAll('inventorinfo')
    for finvent in inventors :


        name = getStringvalue(finvent, 'name')
        eng_name = getStringvalue(finvent, 'engname')
        code = getStringvalue(finvent, 'code')
        address = getStringvalue(finvent, 'address')
        country = getStringvalue(finvent, 'country')
        if ( name == None) :
            continue

        psql = """INSERT INTO KiprisPersonInfo (NAME, ENG_NAME, CODE, ADDRESS, COUNTRY, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s, %s, %s, now(), %s, %s)"""
        pval = (name, eng_name, code, address, country,  lastupdate_date, create_user_id)
        mycursor.execute(psql, pval)

        try:
            persql = """SELECT MAX(PERSON_ID) FROM KiprisPersonInfo"""
            mycursor.execute(persql)
            perio = mycursor.fetchone()[0]
        except:
            perio = 0

        persql = """INSERT INTO KiprisBiblioPersonInfo (BIBLIO_ID, PERSON_ID, TYPE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s,%s, now(), %s, %s)"""
        perval = (biblio, perio, 'inventor',  lastupdate_date, create_user_id)
        #이거 확인
        mycursor.execute(persql, perval)



    applicants = soup.findAll('applicantinfo')
    for fapplicant in applicants :
        name = getStringvalue(fapplicant, 'name')
        eng_name = getStringvalue(fapplicant, 'engname')
        code = getStringvalue(fapplicant, 'code')
        address = getStringvalue(fapplicant, 'address')
        country = getStringvalue(fapplicant, 'country')

        if ( name == None) :
            continue

        psql = """INSERT INTO KiprisPersonInfo (NAME, ENG_NAME, CODE, ADDRESS, COUNTRY, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s, %s, %s, now(), %s, %s)"""
        pval = (name, eng_name, code, address, country, lastupdate_date, create_user_id)
        mycursor.execute(psql, pval)

        try:
            persql = """SELECT MAX(PERSON_ID) FROM KiprisPersonInfo"""
            mycursor.execute(persql)
            perio = mycursor.fetchone()[0]
        except:
            perio = 0

        persql = """INSERT INTO KiprisBiblioPersonInfo (BIBLIO_ID, PERSON_ID, TYPE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s,%s, now(), %s, %s)"""
        perval = (biblio, perio, 'applicant',  lastupdate_date, create_user_id)
        #이거 확인
        mycursor.execute(persql, perval)

    agents = soup.findAll('agentinfo')
    for fagent in agents :
        name = getStringvalue(fagent, 'name')
        eng_name = getStringvalue(fagent, 'engname')
        code = getStringvalue(fagent, 'code')
        address = getStringvalue(fagent, 'address')
        country = getStringvalue(fagent, 'country')

        if ( name == None) :
            continue

        psql = """INSERT INTO KiprisPersonInfo (NAME, ENG_NAME, CODE, ADDRESS, COUNTRY, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s, %s, %s, now(), %s, %s)"""
        pval = (name, eng_name, code, address, country,  lastupdate_date, create_user_id)
        mycursor.execute(psql, pval)

        try:
            persql = """SELECT MAX(PERSON_ID) FROM KiprisPersonInfo"""
            mycursor.execute(persql)
            perio = mycursor.fetchone()[0]
        except:
            perio = 0

        persql = """INSERT INTO KiprisBiblioPersonInfo (BIBLIO_ID, PERSON_ID, TYPE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s,%s, now(), %s, %s)"""
        perval = (biblio, perio, 'agent',  lastupdate_date, create_user_id)
        #이거 확인
        mycursor.execute(persql, perval)

    #KiprisPriorDocumentInfo
    priorartdocuments = soup.findAll('priorartdocumentsinfo')
    for fpriorartdocument in priorartdocuments :
        document_number = getStringvalue(fpriorartdocument, 'documentsnumber')

        if ( document_number == None) :
            continue

        pdsql = """INSERT INTO KiprisPriorDocumentInfo (DOCUMENT_NUMBER, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s,now(),%s,%s)"""
        pdval = (document_number, lastupdate_date, create_user_id)
        mycursor.execute(pdsql, pdval)

        try:
            docsql = """SELECT MAX(DOCUMENT_ID) FROM KiprisPriorDocumentInfo"""
            mycursor.execute(docsql)
            docio = mycursor.fetchone()[0]
        except:
            docio = 0

        docuisql = """INSERT INTO KiprisBiblioPriorDocumentInfo (BIBLIO_ID, DOCUMENT_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        docuival = (biblio, docio, lastupdate_date, create_user_id)
        mycursor.execute(docuisql, docuival)

    #KiprisPriorityInfo
    priorities = soup.findAll('priorityinfo')
    for fpriority in priorities :
        priority_application_country = getStringvalue(fpriority, 'priorityapplicationcountry')
        priority_application_number = getStringvalue(fpriority, 'priorityapplicationnumber')
        priority_application_date = getStringvalue(fpriority, 'priorityapplicationdate')

        if ( priority_application_number == None) :
            continue

        prsql = """INSERT INTO KiprisPriorityInfo (APPLICATION_COUNTRY, APPLICATION_NUMBER, APPLICATION_DATE, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s,now(), %s, %s)"""
        prval = (priority_application_country, priority_application_number, priority_application_date,  lastupdate_date, create_user_id)
        mycursor.execute(prsql, prval)

        try:
            prioritsql = """SELECT MAX(PRIORITY_ID) FROM KiprisPriorityInfo"""
            mycursor.execute(prioritsql)
            priorio = mycursor.fetchone()[0]
        except:
            priorio = 0

        prioriisql = """INSERT INTO KiprisBiblioPriorityInfo (BIBLIO_ID, PRIORITY_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        prioriival = (biblio, priorio,  lastupdate_date, create_user_id)
        mycursor.execute(prioriisql, prioriival)

    #KiprisDesignatedInfo
    designations = soup.findAll('designatedstateinfo')
    for fdesign in designations :
        kind = getStringvalue(fdesign, 'kind')
        country = getStringvalue(fdesign, 'country')

        if ( country == None) :
            continue

        dsql = """INSERT INTO KiprisDesignatedInfo (KIND, COUNTRY, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s,%s,now(),%s,%s)"""
        dval = (kind, country,  lastupdate_date, create_user_id)
        mycursor.execute(dsql, dval)

        try:
            dessql = """SELECT MAX(DESIGNATED_ID) FROM KiprisDesignatedInfo"""
            mycursor.execute(dessql)
            desio = mycursor.fetchone()[0]
        except:
            desio = 0

        desisql = """INSERT INTO KiprisBiblioDesignatedInfo (BIBLIO_ID, DESIGNATED_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        desival = (biblio, desio, lastupdate_date, create_user_id)
        mycursor.execute(desisql, desival)

    #KiprisLegalInfo
    legals = soup.findAll('legalstatusinfo')
    for flegal in legals :
        receipt_number = getStringvalue(flegal, 'receiptnumber')
        receipt_date = getStringvalue(flegal, 'receiptdate')
        document_name = getStringvalue(flegal, 'documentname')
        document_eng_name = getStringvalue(flegal, 'documentengname')
        common_code_name = getStringvalue(flegal, 'commoncodename')

        if ( receipt_number == None) :
            continue

        lesql = """INSERT INTO KiprisLegalInfo (RECEIPT_NUMBER, RECEIPT_DATE, DOCUMENT_NAME, DOCUMENT_ENG_NAME, COMMON_CODE_NAME, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s, %s, %s, now(), %s, %s)"""
        leval = (receipt_number, receipt_date, document_name, document_eng_name, common_code_name,  lastupdate_date, create_user_id)
        mycursor.execute(lesql, leval)

        try:
            legsql = """SELECT MAX(LEGAL_ID) FROM KiprisLegalInfo"""
            mycursor.execute(legsql)
            legio = mycursor.fetchone()[0]
        except:
            legio = 0

        legisql = """INSERT INTO KiprisBiblioLegalInfo (BIBLIO_ID, LEGAL_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        legival = (biblio, legio,  lastupdate_date, create_user_id)
        mycursor.execute(legisql, legival)

    #KiprisPathInfo
    pathes = soup.findAll('imagepathinfo')
    for fpath in pathes :
        name = getStringvalue(fpath, 'docname')
        large_path = getStringvalue(fpath, 'largepath')
        path = getStringvalue(fpath, 'path')

        if ( name == None) :
            continue

        isql = """INSERT INTO KiprisImageInfo (NAME, LARGE_PATH, PATH, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, %s, now(), %s, %s)"""
        ival = (name, large_path, path,  lastupdate_date, create_user_id)
        mycursor.execute(isql, ival)

        try:
            imgisql = """SELECT MAX(IMAGE_ID) FROM KiprisImageInfo"""
            mycursor.execute(imgisql)
            imgio = mycursor.fetchone()[0]
        except:
            imgio = 0

        imgiisql = """INSERT INTO KiprisBiblioImageInfo (BIBLIO_ID, IMAGE_ID, CREATE_DATE, LASTUPDATE_DATE, CREATE_USER_ID) VALUES (%s, %s, now(), %s, %s)"""
        imgiival = (biblio, imgio, lastupdate_date, create_user_id)
        mycursor.execute(imgiisql, imgiival)

    index+=1
    mycursor.close()

