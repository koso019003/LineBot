import requests
import random
from flask import Flask, request, abort

import configparser

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

from crawler import *
from dataUtil import *

config = configparser.ConfigParser()
config.read("config.ini")
Channel_Access_Token = config['line_bot']['Channel_Access_Token']
Channel_Secret = config['line_bot']['Channel_Secret']

requests.packages.urllib3.disable_warnings()

app = Flask(__name__)


line_bot_api = LineBotApi(Channel_Access_Token)
parser = WebhookParser(Channel_Secret)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)

        # if event is MessageEvent and message is TextMessage, then echo text
        for event in events:
            if not isinstance(event, MessageEvent):
                if isinstance(event, PostbackEvent):
                    handle_postback(event)
                continue

            if not isinstance(event.message, TextMessage):
                if isinstance(event.message, StickerMessage):
                    handle_sticker_message(event)
                continue

            if event.message.text:
                handle_text_message(event)

    except InvalidSignatureError:
        abort(400)
        return 'Fail'
    return 'OK'


def handle_text_message(event):
    # print(event)
    user_id = event.source.sender_id
    # print(user_id)

    user_cell = find_user_data(user_id)
    user_row = user_cell.row
    # print(user_row)

    my_user = User()

    my_user.idd, my_user.password, my_user.state = get_data([(user_row, sheet_class.index('學號')),
                                                             (user_row, sheet_class.index('密碼')),
                                                             (user_row, sheet_class.index('state'))])
    my_user.state = int(my_user.state)
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)

    user_message = event.message.text

    if my_user.state != 0:
        # 輸入帳號
        if my_user.state == 3:
            my_user.idd = user_message
            update_sheet(my_user.idd, loc=(user_row, my_user.state))
            content = '你的帳號為:{}'.format(my_user.idd)

        # 輸入密碼
        elif my_user.state == 4:
            my_user.password = user_message
            update_sheet(my_user.password, loc=(user_row, my_user.state))
            content = '你的密碼為:{}'.format(my_user.password)

        # 輸入工作一內容
        elif my_user.state == 5:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        # 輸入工作二內容
        elif my_user.state == 6:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        # 輸入工作三內容
        elif my_user.state == 7:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        # 輸入工作四內容
        elif my_user.state == 8:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        # 輸入工作五內容
        elif my_user.state == 9:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        # 輸入工作六內容
        elif my_user.state == 10:
            w_c = user_message
            update_sheet(w_c, loc=(user_row, my_user.state))
            content = '已設定工作 {} 的內容為: {}'.format(my_user.state - 4, w_c)

        else:
            content = '系統發生錯誤'

        update_sheet('0', loc=(user_row, 1))

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=content))
        return 0

    if user_message == '我不玩了':

        # 刪除表單內容
        delete_user(user_id)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='好吧'))
        return 0

    if user_message == '確認帳密':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='你的帳號:{}\n你的密碼:{}'.format(my_user.idd, my_user.password)))
        return 0

    if user_message == '立即簽到簽退':
        work_list = total_work(my_user.idd, my_user.password, 'get_work_list')
        columns_work = []
        # print(work_list)
        for i in work_list:
            a_text = '{}. '.format(i[0]) + i[1]
            # print(a_text)
            columns_work.append(
                CarouselColumn(
                    # thumbnail_image_url='https://example.com/item1.jpg',
                    text=a_text,
                    actions=[
                        PostbackTemplateAction(
                            label='簽到',
                            data='work_{}_signIn_{}'.format(i[0], user_row)
                        ),
                        PostbackTemplateAction(
                            label='簽退',
                            data='work_{}_signOut_{}'.format(i[0], user_row)
                        ),
                        PostbackTemplateAction(
                            label='設定工作內容',
                            data='setWork_{}_{}'.format(i[0], user_row)
                        )
                    ])
            )

        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=columns_work
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

        return 0

    if user_message == '預約簽到簽退':
        work_list = total_work(my_user.idd, my_user.password, 'get_work_list')
        columns_work = []
        # print(work_list)
        for i in work_list:
            a_text = '{}. '.format(i[0]) + i[1]
            # print(a_text)
            columns_work.append(
                CarouselColumn(
                    # thumbnail_image_url='https://example.com/item1.jpg',
                    text=a_text,
                    actions=[
                        DatetimePickerTemplateAction(
                            label='預約簽到',
                            data='work_{}_schedSignIn_{}'.format(i[0], user_row),
                            mode='datetime'
                        ),
                        DatetimePickerTemplateAction(
                            label='預約簽退',
                            data='work_{}_schedSignOut_{}'.format(i[0], user_row),
                            mode='datetime'
                        ),
                        PostbackTemplateAction(
                            label='取消所有預約',
                            data='work_{}_killSched_{}'.format(i[0], user_row),
                        ),
                    ])
            )

        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=columns_work
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

        return 0

    if user_message == '定時簽到簽退':
        line_bot_api.push_message(user_id, TextSendMessage(
            text='注意喔! 這個任務是每周同一時間進行，這裡設定的會是開始時間'))

        work_list = total_work(my_user.idd, my_user.password, 'get_work_list')
        columns_work = []
        # print(work_list)
        for i in work_list:
            a_text = '{}. '.format(i[0]) + i[1]
            # print(a_text)
            columns_work.append(
                CarouselColumn(
                    # thumbnail_image_url='https://example.com/item1.jpg',
                    text=a_text,
                    actions=[
                        DatetimePickerTemplateAction(
                            label='定時簽到',
                            data='work_{}_timingSignIn_{}'.format(i[0], user_row),
                            mode='datetime'
                        ),
                        DatetimePickerTemplateAction(
                            label='定時簽退',
                            data='work_{}_timingSignOut_{}'.format(i[0], user_row),
                            mode='datetime'
                        ),
                        PostbackTemplateAction(
                            label='取消所有定時任務',
                            data='work_{}_killTiming_{}'.format(i[0], user_row),
                        )
                    ])
            )

        carousel_template_message = TemplateSendMessage(
            alt_text='Carousel template',
            template=CarouselTemplate(
                columns=columns_work
            )
        )
        line_bot_api.reply_message(event.reply_token, carousel_template_message)

        return 0

    column_list = [
        CarouselColumn(
            title='帳號設定',
            text='先設定過帳號才能用喔!',
            actions=[
                PostbackTemplateAction(
                    label='設定帳號',
                    data='setID_{}'.format(user_row)
                ),
                PostbackTemplateAction(
                    label='設定密碼',
                    data='setPassword_{}'.format(user_row)
                ),
                MessageTemplateAction(
                    label='確認帳密',
                    text='確認帳密'
                )])]

    if total_work(my_user.idd, my_user.password, 'check_user_exist'):

        column_list.insert(
            0,
            CarouselColumn(
                title='登入成功',
                text='請從以下選擇服務',
                actions=[
                    MessageTemplateAction(
                        label='立即簽到簽退',
                        text='立即簽到簽退'
                    ),
                    MessageTemplateAction(
                        label='預約簽到簽退',
                        text='預約簽到簽退'
                    ),
                    MessageTemplateAction(
                        label='定時簽到簽退',
                        text='定時簽到簽退'
                    )
                ]))

    carousel_template_message = TemplateSendMessage(
        alt_text='Carousel template',
        template=CarouselTemplate(
            columns=column_list
        )
    )

    line_bot_api.reply_message(event.reply_token, carousel_template_message)

    return 0


def handle_postback(event):
    user_id = event.source.sender_id
    post_data = event.postback.data
    # print(post_data)
    if post_data.split('_')[0] == 'setID':
        user_row = int(post_data.split('_')[1])
        update_sheet('3', (user_row, 1))

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='請輸入你的學號'))
        return 0
    if post_data.split('_')[0] == 'setPassword':
        user_row = int(post_data.split('_')[1])
        update_sheet('4', (user_row, 1))

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='請輸入你的portal密碼'))
        return 0
    if post_data.split('_')[0] == 'setWork':
        user_row = int(post_data.split('_')[2])
        target = int(post_data.split('_')[1])
        update_sheet(target + 4, (user_row, 1))

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='請輸入工作內容'))
        return 0

    if post_data.split('_')[0] == 'work':
        user_row = int(post_data.split('_')[3])
        target = int(post_data.split('_')[1])

        idd, pas, attend_work = get_data([(user_row, sheet_class.index('學號')),
                                          (user_row, sheet_class.index('密碼')),
                                          (user_row, target + 4)])

        if post_data.split('_')[2] == 'signIn':
            contents = total_work(idd, pas, 'check_in', target)

        elif post_data.split('_')[2] == 'signOut':
            if attend_work == '':
                contents = '請先設定工作內容'
            else:
                contents = total_work(idd, pas, 'check_out', target, attend_work)

        elif post_data.split('_')[2] == 'schedSignIn':
            schedule_time = event.postback.params['datetime']
            success = write_schedule(schedule_time, user_id, idd, pas, 'check_in', target, is_timing=0)

            schedule_time = ' '.join(schedule_time.split('T'))
            if success:
                contents = '已預約 {} 簽到'.format(schedule_time)
            else:
                contents = '未成功預約 {} 簽到'.format(schedule_time)

        elif post_data.split('_')[2] == 'schedSignOut':
            if attend_work == '':
                contents = '請先設定工作內容:'
                update_sheet(target + 4, (user_row, 1))
            else:
                schedule_time = event.postback.params['datetime']
                success = write_schedule(schedule_time, user_id, idd, pas,
                                         'check_out', target, attend_work, is_timing=0)

                schedule_time = ' '.join(schedule_time.split('T'))
                if success:
                    contents = '已預約 {} 簽退'.format(schedule_time)
                else:
                    contents = '未成功預約 {} 簽退'.format(schedule_time)

        elif post_data.split('_')[2] == 'killSched':
            contents = kill_schedule(user_id, is_timing=0)

            contents = '取消工作 {} 所有預約'.format(target) + contents

        elif post_data.split('_')[2] == 'timingSignIn':
            schedule_time = event.postback.params['datetime']
            success = write_schedule(schedule_time, user_id, idd, pas, 'check_in', target, is_timing=1)

            schedule_time = ' '.join(schedule_time.split('T'))
            if success:
                contents = '已定時預約 {} 簽到'.format(schedule_time)
            else:
                contents = '未成功定時預約 {} 簽到'.format(schedule_time)

        elif post_data.split('_')[2] == 'timingSignOut':
            if attend_work == '':
                contents = '請先設定工作內容:'
                update_sheet(target + 4, (user_row, 1))
            else:
                schedule_time = event.postback.params['datetime']
                success = write_schedule(schedule_time, user_id, idd, pas,
                                         'check_out', target, attend_work, is_timing=1)

                schedule_time = ' '.join(schedule_time.split('T'))
                if success:
                    contents = '已定時預約 {} 簽退'.format(schedule_time)
                else:
                    contents = '未成功定時預約 {} 簽退'.format(schedule_time)

        elif post_data.split('_')[2] == 'killTiming':

            contents = kill_schedule(user_id, is_timing=1)

            contents = '取消工作 {} 所有定時任務'.format(target) + contents

        else:
            contents = '系統錯誤'

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=contents))
        return 0


def handle_sticker_message(event):
    # print("package_id:", event.message.package_id)
    # print("sticker_id:", event.message.sticker_id)
    # ref. https://developers.line.me/media/messaging-api/sticker_list.pdf
    sticker_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 21, 100, 101, 102, 103, 104, 105, 106,
                   107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125,
                   126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 401, 402]
    index_id = random.randint(0, len(sticker_ids) - 1)
    sticker_id = str(sticker_ids[index_id])
    # print(index_id)
    sticker_message = StickerSendMessage(
        package_id='1',
        sticker_id=sticker_id
    )
    line_bot_api.reply_message(
        event.reply_token,
        sticker_message)


if __name__ == '__main__':
    app.run()
