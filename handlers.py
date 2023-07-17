from telegram.ext import CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from config import MANAGER_CHAT_ID
from googleapiclient.discovery import build
from google.oauth2.service_account import ServiceAccountCredentials
from config import SPREADSHEET_ID, SERVICE_ACCOUNT_FILE



def read_tasks_from_sheet():
    # Настройка авторизации
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, ['https://www.googleapis.com/auth/spreadsheets'])
    service = build('sheets', 'v4', credentials=credentials)

    # Загрузка данных из таблицы
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range='Sheet1').execute()
    values = result.get('values', [])

    tasks = []

    # Обработка данных
    if len(values) > 1:
        for row in values[1:]:
            tel_id = row[0]
            text = row[1]
            date = row[2]
            time = row[3]
            answer_time = int(row[4])

            task_data = {
                'tel_id': tel_id,
                'text': text,
                'date': date,
                'time': time,
                'answer_time': answer_time
            }

            tasks.append(task_data)

    return tasks


def button(update, context):
    query = update.callback_query
    task_data = query.data.split(',')  # Предполагается, что данные о задаче в формате "tel_id,text,date,time,answer_time"

    tel_id = task_data[0]
    text = task_data[1]
    date = task_data[2]
    time = task_data[3]
    answer_time = int(task_data[4])

    keyboard = [
        [InlineKeyboardButton("Выполнено", callback_data=f"выполнено,{tel_id}"),
         InlineKeyboardButton("Не Выполнено", callback_data=f"не выполнено,{tel_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=tel_id, text=text, reply_markup=reply_markup)

    # Запуск задачи проверки таймаута
    job = context.job_queue.run_once(check_timeout, answer_time, context=tel_id)
    context.chat_data[f"job_{tel_id}"] = job


def check_timeout(context):
    tel_id = context.job.context
    response = "Работник проигнорировал."

    context.bot.send_message(chat_id=MANAGER_CHAT_ID, text=response)
    del context.chat_data[f"job_{tel_id}"]


button_handler = CallbackQueryHandler(button)
check_timeout_handler = CallbackQueryHandler(check_timeout)


