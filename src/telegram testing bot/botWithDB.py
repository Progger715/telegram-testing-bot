import datetime

import telebot
from telebot import types
import DBHelper
import localData

bot = telebot.TeleBot(localData.token)
cur_group_student = ''  # группа текущего сеанса
cur_name = ''  # имя пользователя текущего сеанса
cur_id_users = ''
cur_passwords = ''  # id текущего сеанса
cur_id_test = ''  # id текущего теста
flag_authorized = False  # пройдена ли авторизация
flag_given_answer = False  # получен ли ответ на текущий вопрос
answers = []  # ответы пользователя
cur_answer = -1  # ответ на текущий вопрос


# sessions = {
#     'telegram_user_id': {
#
#     }
# }
#

# dict = {
#   'user1-chat-id': {
#      'api_key': 'ключ1',
#      'profile_id': 'id1'
#   },
#   'user2-chat-id': {
#      'api_key': 'ключ2',
#      'profile_id': 'id2'
#   },
# }
#
#
# cur_data = {
#     'chat_id': {
#         'group': '3932',
#
#     }
# }

# @bot.message_handler(content_types='text')
# def text_handler(message):
#     pass


@bot.message_handler(commands=['start'])
def start(message):
    print(type('asdfg'))
    print("id = ", type(message.chat.id))
    print(message.from_user.id)
    print(message)
    bot.send_message(message.chat.id, 'Вы запустили бота!')


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Вы остановили бота!')


@bot.message_handler(commands=['admin'])
def admin(message):
    global flag_authorized
    flag_authorized = True
    global cur_group_student
    cur_group_student = '3932'
    global cur_name
    cur_name = 'Егор Крикунов'
    global cur_id_users
    cur_id_users = '0001'
    bot.send_message(message.chat.id,
                     f'Добро пожаловать, {cur_name}!' + ' Вы успешно авторизовались. '
                                                        'Теперь Вы можете ознакомиться с доступными для Вас '
                                                        'тестами (/check_available_tests).')


@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.send_message(message.chat.id, 'Вы находитесь в главном меню')


@bot.message_handler(commands=['login'])
def login(message):
    group = bot.send_message(message.chat.id, 'отправьте номер своей группы:')
    bot.register_next_step_handler(group, get_number_group)


def get_number_group(message):
    if DBHelper.checking_group_availability(message.text):
        global cur_group_student
        cur_group_student = message.text
        name = bot.send_message(message.chat.id, 'Отправьте свое имя и фамилию:')
        bot.register_next_step_handler(name, get_name_student)
    elif message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы прервали операцию авторизации.')
    else:
        msg = bot.send_message(message.chat.id,
                               "Такая группа не обнаружена в базе данных. "
                               "\nПопробуйте ввести номер группы снова:")
        bot.register_next_step_handler(msg, get_number_group)


def get_name_student(message):
    possible_students = DBHelper.get_possible_students(message.text, cur_group_student)
    if len(possible_students) > 0:
        global cur_name
        global cur_passwords
        cur_name = message.text
        cur_passwords = possible_students.copy()
        message_id_student = bot.send_message(message.chat.id,
                                              'отправьте свой пароль'
                                              '(указан в личном кабинете в разделе "Профиль"):')
        bot.register_next_step_handler(message_id_student, get_id_student, possible_students)
    elif message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы прервали операцию авторизации.')
    else:
        msg = bot.send_message(message.chat.id,
                               "Студент не обнаружен в базе данных. "
                               "\nПопробуйте ввести имя и фамилию снова:")
        bot.register_next_step_handler(msg, get_name_student)


def get_id_student(message, possible_students):
    global flag_authorized
    print(possible_students)
    if message.text == possible_students[0]:
        flag_authorized = True
        global cur_id_users
        cur_id_users = possible_students[1]
    if flag_authorized:
        bot.send_message(message.chat.id,
                         f'Добро пожаловать, {cur_name}!' + ' Вы успешно авторизовались. '
                                                            'Теперь Вы можете ознакомиться с доступными для Вас '
                                                            'тестами (/check_available_tests).')
    elif message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы прервали операцию авторизации.')
    else:
        msg = bot.send_message(message.chat.id,
                               "Идентификатор студента введен неверно!"
                               "\nПопробуйте ввести Идентификатор студента снова:")
        bot.register_next_step_handler(msg, get_id_student)


@bot.message_handler(commands=['logout'])
def logout(message):
    global cur_group_student
    global cur_name
    global cur_passwords
    global cur_id_test
    global flag_authorized
    global flag_given_answer
    global answers
    global cur_answer

    cur_group_student = ''
    cur_name = ''
    cur_passwords = ''
    cur_id_test = ''  # id текущего теста
    flag_authorized = False  # пройдена ли авторизация
    flag_given_answer = False  # получен ли ответ на текущий вопрос
    answers = []  # ответы пользователя
    cur_answer = -1  # ответ на текущий вопрос
    bot.send_message(message.chat.id, 'Вы вышли из своего профиля')


@bot.message_handler(commands=['check_available_tests'])
def check_available_test(message):
    if flag_authorized:
        available = DBHelper.get_name_and_id_available_test(cur_group_student)
        # print(available)
        if len(available) > 0:
            markup_inline = types.InlineKeyboardMarkup()
            for i in range(0, len(available)):
                # print(available[i])
                item = types.InlineKeyboardButton(text=available[i][0], callback_data=f'test{available[i][1]}')
                markup_inline.add(item)

            bot.send_message(message.chat.id, 'Вам доступны следующие тесты:', reply_markup=markup_inline)
        else:
            bot.send_message(message.chat.id, 'Для Вас нет доступных тестов!')
    else:
        (bot.send_message(message.chat.id,
                          'Вы не авторизовались. Для просмотра доступных тестов пройдите авторизацию (/login)'))


@bot.callback_query_handler(func=lambda call: True)
def handle_button_presses(call):
    print("call.data = ", call.data)
    if call.data.find('test') != -1:
        send_description_test(call)
    elif call.data == 'start_t':
        start_test(call.message)
    elif call.data.find('answer') != -1:
        process_answer(call.data)
    elif call.data == 'end1':
        save_all_answers(call.message)
    elif call.data == 'end2':
        get_number_edited_answer(call.message)
    try:
        bot.answer_callback_query(callback_query_id=call.id, text='This is a test', show_alert=False)
    except Exception as ex:
        print('[handle_button] bot.answer_callback_query(callback_query_id=call.message.chat.id)', ex)


def send_description_test(call):
    global cur_id_test
    cur_id_test = call.data[4:]
    markup_inline = types.InlineKeyboardMarkup()
    item = types.InlineKeyboardButton(text="Начать", callback_data='start_t')
    markup_inline.add(item)
    bot.send_message(call.message.chat.id, create_description_for_test(), reply_markup=markup_inline)
    bot.answer_callback_query(callback_query_id=call.id)


def create_description_for_test():
    buffer = DBHelper.get_data_for_description_test(cur_id_test)
    # quantity_attempts = DBHelper.get_name_and_quantity_attempts_test(cur_id_test)
    # print(quantity_attempts)
    # if len(quantity_attempts) > 0:
    #     quantity_attempts = quantity_attempts[0][1]
    # else:
    #     quantity_attempts = buffer[0][4]
    description = f"{buffer[0][0]}\n\nКоличество вопросов: {buffer[0][1]}\nКоличество попыток: {buffer[0][2]}\n" \
                  f"Количество оставшихся попыток: {DBHelper.get_remaining_attempts_for_test(cur_id_users, cur_id_test)}\n\n" \
                  f"Описание:\n{buffer[0][3]}\n\nАвтор теста: {buffer[0][4]} "
    # f"Количество оставшихся попыток: {quantity_attempts}\n\n" \

    return description


def process_answer(data):
    # format data: "answer#{number_question}{flag_correctness}_{number_answer}}"
    # example: answer#2_True_1
    print("data = " + data)
    global cur_answer
    global flag_given_answer
    flag_given_answer = True

    index_answer = data.rfind('_') + 1
    cur_answer = int(data[index_answer:])
    print("cur_answer = ", cur_answer)

    index_correctness = data.find('True')
    if index_correctness != -1:
        number_question = int(data[7:index_correctness]) - 1
        print("number_question = ", number_question)
        answers[number_question] = '+'
    print("answers = ", answers, "\n\n")


def save_all_answers(message):
    count_right_answers = answers.count('+')
    remaining_attempts = DBHelper.get_remaining_attempts_for_test(cur_id_users, cur_id_test)
    DBHelper.record_result(cur_id_users, cur_id_test, count_right_answers, datetime.datetime.now(),
                           remaining_attempts - 1)
    format_answer = []
    for i in range(0, len(answers)):
        format_answer.append(f'{i + 1}) {answers[i]}')
    format_answer = '\n'.join(format_answer)
    # data_about_test = DBHelper.get_name_and_quantity_attempts_test(cur_id_test)
    bot.send_message(message.chat.id,
                     f"Ваш результат: {count_right_answers} "
                     f"из {len(answers)} \n{format_answer}")


def get_number_edited_answer(message):
    number = bot.send_message(message.chat.id, 'Введите номер вопроса, в котором хотите изменить ответ:')
    bot.register_next_step_handler(number, edit_answer)


def edit_answer(message):
    if message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы отменили редактирование вопроса')
        end_test(message)
        return
    try:
        number_question = int(message.text)
        question = DBHelper.get_one_question(cur_id_test, number_question)
        print("EDITOR\tquestion = ", question)
        question = f"{number_question}) " + question[0][0]
        send_question(message,
                      question,
                      DBHelper.get_answers_for_one_question(cur_id_test, number_question))
        end_test(message)
    except Exception as ex:
        print('[Error bot] edit_answer(message)\t', ex)
        message = bot.send_message(message.chat.id,
                                   'Вы ввели некорректный номер вопроса! Введите корректный номер вопроса:')
        bot.register_next_step_handler(message, edit_answer)


def send_question(message, question, answers_for_question):
    # def send_question(message, question, buffer_question):
    # buffer_question[0][0] - сам вопрос
    # buffer_question[n][1] - вариант ответа
    # buffer_question[n][2] - правильность варианта ответа
    markup_inline = types.InlineKeyboardMarkup()

    number_answer = 0
    for one_answer in answers_for_question:
        # one_answer[0] - номер вопроса
        # one_answer[1] - вариант ответа
        # one_answer[2] - флаг корректности
        # format data: "answer#{number_question}{flag_correctness}_{number_answer}}"
        item = types.InlineKeyboardButton(text=one_answer[1],
                                          callback_data=f'answer#{one_answer[0]}{one_answer[2]}_{number_answer}')
        markup_inline.add(item)
        number_answer += 1
    # item1 = types.InlineKeyboardButton(text=buffer_question[0][1],
    #                                    callback_data=f'answer1_{answers[2]}_{number_question}')
    # item2 = types.InlineKeyboardButton(text=buffer_question[1][1],
    #                                    callback_data=f'answer2_{buffer_question[1][2]}_{number_question}')
    # item3 = types.InlineKeyboardButton(text=buffer_question[2][1],
    #                                    callback_data=f'answer3_{buffer_question[2][2]}_{number_question}')
    # markup_inline.add(item1)
    # markup_inline.add(item2)
    # markup_inline.add(item3)
    bot.send_message(message.chat.id, question,
                     reply_markup=markup_inline)
    global flag_given_answer
    while not flag_given_answer:
        continue
    bot.send_message(message.chat.id,
                     f"ответ '{answers_for_question[cur_answer][1]}' сохранен")

    flag_given_answer = False


def start_test(message):
    global cur_id_test
    questions = DBHelper.get_all_questions(cur_id_test)
    answers = DBHelper.get_all_answers(cur_id_test)
    init_user_answers(len(questions))
    numbers_answers = 0
    for number_cur_question in range(1, len(questions) + 1, 1):
        buffer_variants_answer_for_to_send = []
        while answers[numbers_answers][0] == number_cur_question:
            buffer_variants_answer_for_to_send.append(answers[numbers_answers])
            numbers_answers += 1
            if numbers_answers >= len(answers):
                break
        question = f'{number_cur_question}) ' + questions[number_cur_question - 1][1]
        send_question(message, question, buffer_variants_answer_for_to_send)
    end_test(message)
    print("test passed")


def end_test(message):
    try:
        end_test_buttons = types.InlineKeyboardMarkup()
        but1 = types.InlineKeyboardButton(text="Сохранить", callback_data='end1')
        but2 = types.InlineKeyboardButton(text="Изменить ответ", callback_data='end2')
        end_test_buttons.add(but1, but2)
        bot.send_message(message.chat.id,
                         'Вы ответили на все вопросы теста. Желаете сохранить ответы и узнать результат?',
                         reply_markup=end_test_buttons)
    except Exception as ex:
        print('[Error PostgreSQL] insert_answers_in_data_base()', ex)


def init_user_answers(quantity):
    global answers
    for i in range(0, quantity, 1):
        answers.append('-')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
