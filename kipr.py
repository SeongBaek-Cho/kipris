import requests
from bs4 import BeautifulSoup

def getStringvalue (item, attr) :
    try :
        return item.find(attr).string.replace("'","''")
    except Exception as ex :
        return None

key = 'Uwsq9QuL9unbs/kiXVJb3RvPs6cB49=LKMhIIt4e8uU='
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
    page_count = int(total_count)/rows
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
    break


applicationnumber_arr = list(set(applicationnumber_arr))
print(applicationnumber_arr)

for number in applicationnumber_arr :
    url = 'http://plus.kipris.or.kr/kipo-api/kipi/patUtiModInfoSearchSevice/getBibliographyDetailInfoSearch?applicationNumber=%s&ServiceKey=%s' %(number, key)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    print(soup)
    item = soup.find('item')
    print(item)


