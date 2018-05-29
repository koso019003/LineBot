from apscheduler.schedulers.blocking import BlockingScheduler
from crawler import *
import pytz
from datetime import datetime, timedelta
import configparser
import urllib3


# for google sheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials as Sac

# for line bot
from linebot import LineBotApi
from linebot.models import *

urllib3.disable_warnings()

config = configparser.ConfigParser()
config.read("config.ini")
Channel_Access_Token = config['line_bot']['Channel_Access_Token']
Channel_Secret = config['line_bot']['Channel_Secret']

GDriveJSON = config['google_sheet']['GDriveJSON']
GSpreadSheet = config['google_sheet']['GSpreadSheet']


line_bot_api = LineBotApi(Channel_Access_Token)


scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', minutes=5)
def timed_job():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        key = Sac.from_json_keyfile_name(GDriveJSON, scope)
        gc = gspread.authorize(key)
        worksheet = gc.open(GSpreadSheet).get_worksheet(1)
    except Exception as ex:
        print('無法連線Google試算表', ex)
        return '無法連線Google試算表'

    print('This job is run every five minutes.')
    record_list = worksheet.col_values(1)[1:]
    print('共有 {} 項預定工作'.format(len(record_list)))

    is_work = []
    # 使用 utc的當前時間
    now = datetime.now(pytz.utc).replace(microsecond=0)
    print('    utc       now:', now)
    for i, r in enumerate(record_list):
        # 初始讀入的時間為台灣時間
        ini_schedule_time = datetime.strptime(r, '%Y-%m-%dT%H:%M')

        # 把讀入的時間換成 utc時間
        schedule_data = ini_schedule_time.replace(tzinfo=pytz.utc)
        schedule_time = schedule_data + timedelta(hours=-8)

        print('schedule time:', schedule_time)

        if schedule_time < now:
            print('doing this work...')
            is_work.append(str(i+1))
            # schedule_data = ['user_id', 'is_timing', '學號', '密碼', '任務', 'target', 'attend work']
            schedule_data = worksheet.row_values(i+2)[1:]
            if len(schedule_data) < 7:
                schedule_data.append('')
            contents = total_work(schedule_data[2], schedule_data[3], schedule_data[4],
                                  int(schedule_data[5]), schedule_data[6])

            worksheet.delete_row(i+2)
            if schedule_data[1] == '1':
                next_schedule_time = ini_schedule_time + timedelta(days=7)
                new_row = [str(next_schedule_time)]
                new_row.extend([i for i in schedule_data if i != ''])
                worksheet.append_row(new_row)
                if schedule_data[4] == 'check_in':
                    schedule_contents = '已預約 {} 簽到'
                else:
                    schedule_contents = '已預約 {} 簽退'
                line_bot_api.push_message(schedule_data[0],
                                          TextSendMessage(text=schedule_contents.format(str(next_schedule_time))))

            line_bot_api.push_message(schedule_data[0], TextSendMessage(text=contents))
    if not is_work:
        print('未執行任何任務')
    else:
        print('執行任務:' + ','.join(is_work))

    return 'success'


if __name__ == '__main__':
    timed_job()
    scheduler.start()
