import gspread
from oauth2client.service_account import ServiceAccountCredentials as Sac
import configparser


class User:

    def __init__(self):
        self.idd = ''
        self.password = ''
        self.state = 0


config = configparser.ConfigParser()
config.read("config.ini")

# GDriveJSON就輸入下載下來Json檔名稱
# GSpreadSheet是google試算表名稱
GDriveJSON = config['google_sheet']['GDriveJSON']
GSpreadSheet = config['google_sheet']['GSpreadSheet']

sheet_class = ['', 'state', 'UserID', '學號', '密碼', '工作一', '工作二', '工作三', '工作四', '工作五']


def delete_user(user_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet1 = gc.open(GSpreadSheet).get_worksheet(0)
        worksheet2 = gc.open(GSpreadSheet).get_worksheet(1)
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    user_id_list = worksheet1.col_values(2)[1:]
    for i, r in enumerate(user_id_list):
        if r == user_id:
            # print('kil from sheet 1', i)
            worksheet1.delete_row(i + 2)

    user_id_list = worksheet2.col_values(2)[1:]
    for i, r in enumerate(user_id_list):
        if r == user_id:
            # print('kil from sheet 2', i)
            worksheet2.delete_row(i + 2)
    return '成功'


# For sheet 1
# loc: (row, col)
def update_sheet(text, loc):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).sheet1
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    worksheet.update_cell(row=loc[0], col=loc[1], value=text)
    # print('更新資料到試算表', GSpreadSheet, loc)
    return 'success'


def find_user_data(user_id):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).sheet1
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    while True:
        try:
            loc = worksheet.find(user_id)
            break
        except gspread.exceptions.CellNotFound:
            worksheet.append_row((0, user_id))
            # print('新增一筆用戶資料到試算表', GSpreadSheet)
            continue

    return loc


def delete_row(row):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).sheet1
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    worksheet.delete_row(row)
    # print('從試算表刪除一筆資料', GSpreadSheet, row)
    return 'success'


# list_of_loc: list of (row, col) => [(row, col), (row, col), ...]
def get_data(list_of_loc):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).sheet1
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    list_of_data = []
    for loc in list_of_loc:
        try:
            data = worksheet.cell(row=loc[0], col=loc[1]).value
            # print('從試算表取得資料', GSpreadSheet, loc)
        except gspread.exceptions.APIError:
            # print('試算表沒有資料')
            data = ''
        list_of_data.append(data)

    return list_of_data


# For sheet 2
def write_schedule(schedule_time, user_id, user_name, pass_word, do_what, target, attend_work='', is_timing=0):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).get_worksheet(1)
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return 0

    worksheet.append_row((schedule_time, user_id, is_timing, user_name, pass_word, do_what, target, attend_work))

    return 1


def kill_schedule(user_id, is_timing=0):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).get_worksheet(1)
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    user_id_list = worksheet.col_values(2)[1:]
    is_timing_list = worksheet.col_values(3)[1:]
    for i, r in enumerate(user_id_list):
        if r == user_id and is_timing_list[i] == str(is_timing):
            # print('kill', i)
            worksheet.delete_row(i + 2)
    return '成功'


# for handel work title out of limit
def get_work_title(work_list):
    return 'a'*30
