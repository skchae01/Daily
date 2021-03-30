# -*- Encoding: utf-8 -*-
import datetime
import requests
import os, sys, platform
import pickle
from bs4 import BeautifulSoup
from datetime import date
from pytz import timezone
from termcolor import colored
from colorama import init
init()
print("*** platform.python_version() => ", platform.python_version())
time_now = datetime.datetime.now(timezone('Asia/Seoul'))
print("*** 현재 시간 : ", str(time_now)[:19])

Day_of_Week = list(u"월화수목금토일")


def findDay(date):
    # born = datetime.datetime.strptime(date, '%Y%m%d').weekday()
    # return (born, calendar.day_name[born])
    born = datetime.datetime.strptime(date, '%Y%m%d').weekday()
    return (Day_of_Week[born]+'요일')


def get_request_query(url, operation, params, serviceKey):
    import urllib.parse as urlparse
    params = urlparse.urlencode(params)
    request_query = url + '/' + operation + '?' + params + '&' + 'serviceKey' + '=' + serviceKey
    return request_query


def print_colored(text, color_char, color_bg):
    print(colored(text, color_char, color_bg))

# 한국천문연구원_천문우주정보__특일_정보제공_서비스 https://data.go.kr/data/15012690/openapi.do
mykey = "R4d%2FrWGREdBR9ALz39coE47YAo6%2B7MlLerPOFkUtoDCZ0cHMNzhfCTDLNxBEayKsq6QqJZGnF%2Bw4VNeH6EgZaw%3D%3D"
url = 'http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService'
year = '2021'

Date_List_filename = 'Date_List_pickle' + year + '.txt'
if os.path.isfile(Date_List_filename):
    # print("이미 특일정보 파일이 있습니다!")
    with open(Date_List_filename, 'rb') as fp:
        Date_List = pickle.load(fp)
        # Date_List = set(Date_List)
else:
    Date_List = []
    for month in range(1, 13):
        if month < 10:
            month = '0' + str(month)
        else:
            month = str(month)
        operation = 'getRestDeInfo'
        params = {'solYear': year, 'solMonth': month}
        request_query = get_request_query(url, operation, params, mykey)
        get_data = requests.get(request_query)
        if get_data.ok:
            soup = BeautifulSoup(get_data.content, 'html.parser')
            item = soup.findAll('item')
            for i in item:
                day = i.locdate.string[-2:]
                # weekname = print_whichday(int(year), int(month), day)
                YYYYMMDD = year + month + day
                weekname = findDay(YYYYMMDD)
                print(i.datename.string, i.isholiday.string, i.locdate.string, weekname)
                Data_dict = {'datename':i.datename.string, 'holiday':i.isholiday.string, 'date':i.locdate.string, 'weekname':weekname}
                Date_List.append(Data_dict)
        operation = 'get24DivisionsInfo'
        params = {'solYear': year, 'solMonth': month}
        request_query = get_request_query(url, operation, params, mykey)
        get_data = requests.get(request_query)
        if get_data.ok:
            soup = BeautifulSoup(get_data.content, 'html.parser')
            item = soup.findAll('item')
            for i in item:
                # day = int(i.locdate.string[-2:])
                day = i.locdate.string[-2:]
                # weekname = print_whichday(int(year), int(month), day)
                YYYYMMDD = year + month + day
                weekname = findDay(YYYYMMDD)
                print(i.datename.string, i.isholiday.string, i.locdate.string, weekname)
                Data_dict = {'datename':i.datename.string, 'holiday':i.isholiday.string, 'date':i.locdate.string, 'weekname':weekname}
                Date_List.append(Data_dict)
    Date_List_filename_plain = 'Date_List_plain' + year + '.txt'
    with open(Date_List_filename_plain, "w") as output:
        output.write(str(Date_List))
    Date_List_filename_pickle = 'Date_List_pickle' + year + '.txt'
    with open(Date_List_filename_pickle, 'wb') as fp:
        pickle.dump(Date_List, fp)

# 오늘이 올해 몇번째 날인지 계산
today_date = date.today()
today_yymmdd = str(today_date).replace("-", "")
this_year = today_yymmdd[0:4]
from_date_yymmdd = this_year + "0101"  # 연초
from_date = datetime.datetime.strptime(from_date_yymmdd, "%Y%m%d").date()
to_date = datetime.datetime.strptime(today_yymmdd, "%Y%m%d").date()
delta_days = to_date - from_date
end_date_yymmdd = this_year + "1231"
end_date = datetime.datetime.strptime(end_date_yymmdd, "%Y%m%d").date()
delta_days2 = end_date - to_date

# 한국천문연구원_천문우주정보_출몰시각정보제공서비스  https://data.go.kr/iim/api/selectAPIAcountView.do
mykey = u"ggCMYx8Gwjo4jeTUp1s0Agyimki9l0L5MqkR1BX58iwP8xxPUpIMcLm0a40ixdDWMk2LS2wYmDL51S2bQKO81Q%3D%3D"  # 출몰시각
url = 'http://apis.data.go.kr/B090041/openapi/service/RiseSetInfoService'
operation = 'getAreaRiseSetInfo'
params = {'location': '서울', 'locdate': today_yymmdd}
request_query = get_request_query(url, operation, params, mykey)
try:
    get_data = requests.get(request_query)
except Exception as e:
    print("requests.get(출몰시각) error occurred: ", e)
    get_data = False
if get_data:
    soup = BeautifulSoup(get_data.content, 'html.parser')
    sunrise_found = soup.find('sunrise')
    if sunrise_found: 
        sunrise = sunrise_found.get_text()
        sunrise_datetime = today_yymmdd + sunrise.strip()
        sunrise_time = datetime.datetime.strptime(sunrise_datetime, "%Y%m%d%H%M")
    sunset_found = soup.find('sunset')
    if sunset_found: 
        sunset = sunset_found.get_text()
        sunset_datetime = today_yymmdd + sunset.strip()
        sunset_time = datetime.datetime.strptime(sunset_datetime, "%Y%m%d%H%M")
    delta_sun = str(sunset_time - sunrise_time)

# What day of the year is it today?
Day_Hangul = findDay(today_yymmdd)
print_colored(f'Hi, Steven!', 'yellow', 'on_blue')
print_colored("오늘은 {:} {}입니다.".format(today_date, Day_Hangul), 'yellow', 'on_blue')
for dict_item in Date_List:
    if dict_item['date'] == today_yymmdd:
        if {dict_item['holiday']} =="Y":
            print_colored(f"오늘은 {dict_item['datename']}이고 공휴일입니다.",'red', 'on_yellow')
        else:
            print_colored(f"오늘은 {dict_item['datename']}이고 공휴일은 아닙니다.", 'blue', 'on_white')
if sunrise_found:
    print("오늘 해뜨는 시각은 {:}:{:}분이고 해지는 시각은 {:}:{:}분입니다.".format(sunrise[0:2], sunrise[2:4], sunset[0:2], sunset[2:4]))
    print(f"해가 떠있는 시간은 {delta_sun[0:2]}시간 {delta_sun[3:5]}분 입니다.")
print("{:}년 한해의 {:,}번째 날입니다! 이제 올해 {:}일 남았습니다.".format(this_year, delta_days.days+1, delta_days2.days))

# if 오후 5시가 넘으면 내일 일출 정보도 표시 
# now_time = datetime.datetime.now()
# now_time_hour = str(now_time.hour)
# now_time_minute = str(now_time.minute)
# now_HHMM = now_time_hour + now_time_minute
now_HHMM = str(time_now).replace("-", "").replace(":", "")[9:13]
print(f"{now_HHMM=}")
if now_HHMM > "1600":
    tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
    tomorrow_yymmdd = str(tomorrow_date).replace("-", "")
    params = {'location': '서울', 'locdate': tomorrow_yymmdd}
    request_query = get_request_query(url, operation, params, mykey)
    try:
        get_data = requests.get(request_query)
    except Exception as e:
        print("requests.get(출몰시각) error occurred: ", e)
        get_data = False
    if get_data:
        soup = BeautifulSoup(get_data.content, 'html.parser')
        sunrise_found = soup.find('sunrise')
        if sunrise_found: sunrise = sunrise_found.get_text()
        sunset_found = soup.find('sunset')
        if sunset_found: sunset = sunset_found.get_text()
        sunrise_datetime = today_yymmdd + sunrise.strip()
        sunrise_time = datetime.datetime.strptime(sunrise_datetime, "%Y%m%d%H%M")
        sunset_datetime = today_yymmdd + sunset.strip()
        sunset_time = datetime.datetime.strptime(sunset_datetime, "%Y%m%d%H%M")
        delta_sun = str(sunset_time - sunrise_time)

    # print_colored(f'Hi, Steven!', 'white', 'on_blue')
    print(" ")
    print_colored("내일은 {:} {}입니다.".format(tomorrow_date, findDay(tomorrow_yymmdd)), 'white', 'on_blue')
    for dict_item in Date_List:
        if dict_item['date'] == tomorrow_yymmdd:
            if {dict_item['holiday']} =="Y":
                print_colored(f"내일은 {dict_item['datename']}이고 공휴일입니다.",'red', 'on_yellow')
            else:
                print_colored(f"내일은 {dict_item['datename']}이고 공휴일은 아닙니다.", 'blue', 'on_white')
    if sunrise_found:
        print("내일 해뜨는 시각은 {:}:{:}분이고 해지는 시각은 {:}:{:}분입니다.".format(sunrise[0:2], sunrise[2:4], sunset[0:2], sunset[2:4]))
        print(f"내일 해가 떠있는 시간은 {delta_sun[0:2]}시간 {delta_sun[3:5]}분 입니다.")
    print("내일은 {:}년 한해의 {:,}번째 날입니다! 올해 {:}일 남습니다.".format(this_year, delta_days.days+2, delta_days2.days-1))

# 기상청 동네예보 통보문 조회서비스  https://data.go.kr/data/15058629/openapi.do
mykey = 'ggCMYx8Gwjo4jeTUp1s0Agyimki9l0L5MqkR1BX58iwP8xxPUpIMcLm0a40ixdDWMk2LS2wYmDL51S2bQKO81Q%3D%3D'
url = 'http://apis.data.go.kr/1360000/VilageFcstMsgService'  # 육상예보조회
operation = 'getLandFcst'
request_query = url + '/' + operation + '?' + 'serviceKey=' +  mykey + '&' + 'numOfRows=10&pageNo=1' + '&' + 'regId=11B10101' # 서울

def Get_ta_rnst_wf(i):
    ta = i.find('ta').get_text()  # 예상기온(℃)
    if ta:
        print(f"{numef_text}", end=" ")
        print(f"예상기온은 {ta}℃ 입니다.", end=" ")
    rnst = i.find('rnst').get_text() # 강수확률
    if rnst:
        if ta: print(f"강수확률 {rnst}% ", end=" ")
        else: print(f"{numef_text} 강수확률 {rnst}% ", end=" ")
    wf = i.find('wf').get_text() # 날씨
    if wf:
       print(f"날씨는 {wf}")

get_data = requests.get(request_query)
if get_data.ok:
    soup = BeautifulSoup(get_data.content, 'html.parser')
    announcetime = soup.find('announcetime').get_text()  # 발표시간
    at_YYYY = announcetime[0:4]
    at_Month = announcetime[4:6]
    at_DD = announcetime[6:8]
    at_HH = announcetime[8:10]
    at_MM = announcetime[10:]
    print(f"\n[기상예보] {at_YYYY}년 {at_Month}월 {at_DD}일 {at_HH}시 {at_MM}분 현재 ")

    item = soup.findAll('item')
    for i in item:
        # print(i)
        numef = i.find('numef').get_text()  # 발효번호
        numef_int = int(numef)
        if numef_int > 1: break

        if at_HH >= "17" or at_HH < "05":
            numef_text = "오늘오후" if numef_int == 0 else "내일오전"
            Get_ta_rnst_wf(i)
        elif at_HH >= "05" and at_HH < "11":
            numef_text = "오늘오전" if numef_int == 0 else "오늘오후"
            Get_ta_rnst_wf(i)

        elif at_HH >= "11" and at_HH < "17":
            numef_text = "오늘오후" if numef_int == 0 else "내일오전"
            Get_ta_rnst_wf(i)
        else:
            print("Something Wrong!")
else:
    print(f"get_data.ok: {get_data.ok}")

# 한국환경공단_미세먼지
# url = 'http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc'
url = 'http://apis.data.go.kr/B552584/ArpltnStatsSvc'
operation = 'getCtprvnMesureLIst' # 시도별 실시간 평균정보 조회
request_query = url + '/' + operation + '?' + 'itemCode=PM10&dataGubun=HOUR&searchCondition=WEEK&pageNo=1&numOfRows=10&ServiceKey=' + mykey
get_data = requests.get(request_query)
if get_data.ok:
    soup = BeautifulSoup(get_data.content, 'html.parser')
    resultcode = soup.find('resultcode')
    # if resultcode:
    #     resultcode = resultcode.get_text()
    # if resultcode != "00":
    #     print(f"*** 결과코드 에러:{resultcode}")
    #     sys.exit()
    resultmsg = soup.find('resultmsg').get_text()
    if resultmsg == "NORMAL_CODE":
        pass
    # elif resultcode == "20":
    #     print(f"*** 결과코드 에러:{resultcode}: 서비스 접근 거부 => 활용 신청하지 않은 OpenAPI 호출")
    #     sys.exit()
    else:
        # resultmsg = soup.find('resultmsg').get_text()  # 결과코드 메시지
        print(f"*** 결과코드 에러:{resultmsg}")
        sys.exit()

    print("\n************************ 미세먼지정보 *************************")
    datatime = soup.find('datatime').get_text()  # 측정일시
    print(f"미세먼지(PM10) 측정일시: {datatime}", end=" ")
    itemcode = soup.find('itemcode').get_text()  # 조회항목
    print(f"조회항목: {itemcode}")
    # datagubun = soup.find('datagubun').get_text()  # 조회항목
    # print(f"자료구분: {datagubun}")
    seoul = soup.find('seoul').get_text()  # 서울 지역 평균
    seoul_int = int(seoul)
    if seoul_int <= 30:
        score = "좋음"
    elif seoul_int > 30 and seoul_int <= 80:
        score = "보통"
    elif seoul_int > 80 and seoul_int <= 110:
        score = "약간 나쁨"
    elif seoul_int > 110 and seoul_int <= 150:
        score = "나쁨"
    else:
        score = "매우나쁨"
    print(f"서울 지역 실시간 시간당 평균: {seoul}㎍/㎥ => {score}")
    print("PM10 판단기준: 좋음 0~30|보통 31~80|나쁨 81~150|매우나쁨 151~")
    print('주의보 => 미세먼지(PM10) 시간당 평균 농도 150㎍/㎥ 이상(2시간 지속)')
    print('경  보 => 미세먼지(PM10) 시간당 평균 농도 300㎍/㎥ 이상(2시간 지속)')
    # print("")
#     print("**************************** 참고 *****************************")
#     print("사람 머리카락 크기: 50~70 마이크로미터(ųm) = 1000분의 1밀리미터")
#     print("미세먼지(PM10)의 크기: 10 마이크로미터(ųm) = 1000분의 1밀리미터")
#     print("***************************************************************")
else:
    print(f"get_data.ok: {get_data.ok}")

print_colored("Have a nice day!!", 'yellow', 'on_blue')
input("")
