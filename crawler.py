import requests
import time
import urllib3
from bs4 import BeautifulSoup
from datetime import datetime
import sched
import configparser

urllib3.disable_warnings()


config = configparser.ConfigParser()
config.read("config.ini")
my_agent = config['agent']['my_agent']


def get_work_token(html_text):
    bb = BeautifulSoup(html_text, "html.parser")
    # print(bb)
    _token = bb.find_all('input', {'name': '_token'})[0].get('value')
    # print(_token)
    return _token


def get_work_list(html_text):
    bb = BeautifulSoup(html_text, "html.parser")

    work_table = bb.select('#table1')[0]
    work_table = work_table.select('tr')

    work_id = []
    for wt in work_table[1:]:
        work_id.append(wt.select('a')[0].get('href').split('=')[-1])

    work_list = [k.text.strip().split('\n') for k in work_table[1:]]

    return work_id, work_list


# check_user_exist、get_work_list、check_in、check_out
def total_work(user_name, pass_word, do_what, target=None, attend_work=None):
    """

    :param user_name:  學號
    :param pass_word:  protal 密碼
    :param do_what:  選擇工作：check_user_exist、get_work_list、check_in、check_out
    :param target:  目標簽到或簽退的工作
    :param attend_work:  目標簽退的工作內容
    :return:
    """

    session = requests.session()

    # ----------------------------登入portal----------------------------------
    log_in_url = 'https://portal.ncu.edu.tw/j_spring_security_check'
    log_in_header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Length': '44',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'NID=iCLUuQomCBj_qlpQcwTpxb7BraYuYZJROnUDKo.wSbXiD4mZsVhw0ZHzClaMFC' +
                  'AzdWEtAKTOjL9WnPahNmHrxN1KNB3; JSESSIONID=511CD3C8D38FAE0B935B11228CCD2F9A',
        'Host': 'portal.ncu.edu.tw',
        'Origin': 'https://portal.ncu.edu.tw',
        'Referer': 'https://portal.ncu.edu.tw/login',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': my_agent
    }
    log_in_form_data = {'j_username': user_name,
                        'j_password': pass_word}
    response = session.post(log_in_url, data=log_in_form_data, headers=log_in_header)
    response = BeautifulSoup(response.text, "html.parser")
    # ----------------------------登入portal----------------------------------

    if len(response.text) < 6000:
        print('登入失敗 :帳號或密碼不正確')
        is_in = False
        session.close()
        # =========================任務1：確認是否可以成功登入=======================
        if do_what == 'check_user_exist':
            session.close()
            return is_in
        # =========================任務1：確認是否可以成功登入=======================
        return '登入失敗 :請確認你的帳號密碼，沒有問題請再試一次'
    else:
        print('登入成功')
        is_in = True
        # =========================任務1：確認是否可以成功登入=======================
        if do_what == 'check_user_exist':
            session.close()
            return is_in
        # =========================任務1：確認是否可以成功登入=======================

    # ----------------------進入人事系統取得工作 & token---------------------------

    # time.sleep(2)
    human_sys_url = 'https://cis.ncu.edu.tw/HumanSys/login?netid-user={}'.format(user_name)
    next_url = 'https://cis.ncu.edu.tw/HumanSys/student/stdSignIn'
    _ = session.get(human_sys_url, stream=True, verify=False)

    # time.sleep(1)
    human_sys = session.get(next_url, stream=True, verify=False)
    human_sys = human_sys.text

    work_id_list, work_list = get_work_list(human_sys)

    # =========================任務2：取得工作清單=======================
    if do_what == 'get_work_list':
        session.close()
        return work_list
    # =========================任務2：取得工作清單=======================

    now_token = get_work_token(human_sys)

    # ----------------------進入人事系統取得工作 & token---------------------------

    # ----------------------進入特定工作簽到或簽退---------------------------------
    if target not in work_id_list:
        try:
            target = work_id_list[target - 1]
        except IndexError:
            print('target out of work_id_list')
            session.close()
            return 0

    # time.sleep(2)

    target_work_url = 'https://cis.ncu.edu.tw/HumanSys/student/stdSignIn/create?ParttimeUsuallyId={}'
    target_work = session.get(target_work_url.format(target), stream=True, verify=False)
    target_work = target_work.text

    target_work = BeautifulSoup(target_work, "html.parser")
    id_no = target_work.find_all('input', {'id': 'idNo'})
    if id_no:
        id_no = id_no[0].get('value')
    else:
        id_no = None
    # ----------------------進入特定工作簽到或簽退---------------------------------

    def do_check_in():
        # time.sleep(2)
        check_in_url = 'https://cis.ncu.edu.tw/HumanSys/student/stdSignIn_detail'
        check_in_from_data = {'functionName': 'doSign',
                              'idNo': id_no,
                              'ParttimeUsuallyId': target,
                              'AttendWork': '',
                              '_token': now_token}
        check_in_header = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                           'Accept-Encoding': 'gzip, deflate, br',
                           'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                           'Connection': 'keep-alive',
                           'Content-Length': '109',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'cis.ncu.edu.tw',
                           'Origin': 'https://cis.ncu.edu.tw',
                           'Referer': 'https://cis.ncu.edu.tw/HumanSys' +
                                      '/student/stdSignIn/create?ParttimeUsuallyId={}'.format(target),
                           'User-Agent': my_agent,
                           'X-Requested-With': 'XMLHttpRequest'}
        check_in_response = session.post(check_in_url, data=check_in_from_data, headers=check_in_header)
        result = check_in_response.json()
        print('check In:', result)
        return result

    def do_check_out(attend_work_):

        # time.sleep(2)
        check_out_url = 'https://cis.ncu.edu.tw/HumanSys/student/stdSignIn_detail'
        check_out_from_data = {'functionName': 'doSign',
                               'idNo': id_no,
                               'ParttimeUsuallyId': target,
                               'AttendWork': attend_work_,
                               '_token': now_token}
        check_out_header = {'Accept': 'application/json, text/javascript, */*; q=0.01',
                            'Accept-Encoding': 'gzip, deflate, br',
                            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                            'Connection': 'keep-alive',
                            'Content-Length': '151',
                            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                            'Host': 'cis.ncu.edu.tw',
                            'Origin': 'https://cis.ncu.edu.tw',
                            'Referer': 'https://cis.ncu.edu.tw/HumanSys/student/stdSignIn' +
                                       '/create?ParttimeUsuallyId={}&msg=signin_ok'.format(target),
                            'User-Agent': my_agent,
                            'X-Requested-With': 'XMLHttpRequest'}
        check_out_response = session.post(check_out_url, data=check_out_from_data, headers=check_out_header)
        # print(check_out_response.json())
        result = check_out_response.json()
        print('check In:', result)
        return result

    if id_no:
        if do_what == 'check_out':
            if attend_work is not None:
                # print('這個工作之前已簽到到過了，自動進行簽退')
                do_check_out(attend_work)
                session.close()
                return '幫你簽退了喔~'
            else:
                session.close()
                return '請填入工作內容'
        else:
            # print('這個工作之前已簽到到過了')
            session.close()
            return '這個工作之前已簽到到過了'
    else:
        if do_what == 'check_in':
            # print('這個工作之前還沒簽到，自動進行簽到')
            do_check_in()
            session.close()
            return '幫你簽到了喔~'
        else:
            # print('這個工作之前還沒簽到')
            session.close()
            return '這個工作之前還沒簽到'
