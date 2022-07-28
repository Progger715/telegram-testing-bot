import telebot
from telebot import types
import DBHelper
import localData

bot = telebot.TeleBot(localData.token)
cur_group_student = ''  # группа текущего сеанса
cur_name = ''  # имя пользователя текущего сеанса
cur_id = ''  # id текущего сеанса
cur_id_test = ''  # id текущего теста
flag_authorized = False  # пройдена ли авторизация
flag_get_answer = False  # получен ли ответ на текущий вопрос
answers = []  # ответы пользователя
cur_answer = -1  # ответ на текущий вопрос


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Вы запустили бота!')


@bot.message_handler(commands=['stop'])
def stop(message):
    bot.send_message(message.chat.id, 'Вы остановили бота!')


@bot.message_handler(commands=['admin'])
def admin(message):
    # get_id_student(message)
    global flag_authorized
    flag_authorized = True
    global cur_group_student
    cur_group_student = '3932'


@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.send_message(message.chat.id, 'Вы находитесь в главном меню')


@bot.message_handler(commands=['login'])
def login(message):
    group = bot.send_message(message.chat.id, 'отправьте номер своей группы:')
    bot.register_next_step_handler(group, get_number_group)


@bot.message_handler(commands=['logout'])
def logout(message):
    global cur_group_student
    global cur_name
    global cur_id
    global cur_id_test
    global flag_authorized
    global flag_get_answer
    global answers
    global cur_answer

    cur_group_student = ''
    cur_name = ''
    cur_id = ''
    cur_id_test = ''  # id текущего теста
    flag_authorized = False  # пройдена ли авторизация
    flag_get_answer = False  # получен ли ответ на текущий вопрос
    answers = []  # ответы пользователя
    cur_answer = -1  # ответ на текущий вопрос
    group = bot.send_message(message.chat.id, 'Вы вышли из своего профиля')


def get_number_group(message):
    if len(DBHelper.find_in_group(message.text)) > 0:  # message.text == '3932':
        # bot.send_message(message.chat.id, f"your group = {message.text}")
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
    buf_id = DBHelper.find_id_student(cur_group_student, message.text)
    if len(buf_id) > 0:
        global cur_name
        global cur_id
        cur_name = message.text
        cur_id = buf_id[0][0]
        # print("qur_id = ", buf_id)
        id_student = bot.send_message(message.chat.id,
                                      'отправьте свой Идентификатор студента '
                                      '(указан в личном кабинете в разделе "Профиль"):')
        bot.register_next_step_handler(id_student, get_id_student)
    elif message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы прервали операцию авторизации.')
    else:
        msg = bot.send_message(message.chat.id,
                               "Студент не обнаружен в базе данных. "
                               "\nПопробуйте ввести имя и фамилию снова:")
        bot.register_next_step_handler(msg, get_name_student)


def get_id_student(message):
    if message.text == cur_id:
        global flag_authorized
        flag_authorized = True
        bot.send_message(message.chat.id,
                         f'добро пожаловать, {cur_name}!' + ' Вы успешно авторизовались. '
                                                            'Теперь Вы можете ознакомиться с доступными для Вас тестами '
                                                            ' (/check_available_tests).')
    elif message.text == '/cancel':
        bot.send_message(message.chat.id, 'Вы прервали операцию авторизации.')
    else:
        msg = bot.send_message(message.chat.id,
                               "Идентификатор студента введен неверно!"
                               "\nПопробуйте ввести Идентификатор студента снова:")
        bot.register_next_step_handler(msg, get_id_student)


@bot.message_handler(commands=['check_available_tests'])
def check_available_test(message):
    if flag_authorized:
        available = DBHelper.find_available_test(cur_group_student)
        if len(available) > 0:
            markup_inline = types.InlineKeyboardMarkup()
            for i in range(0, len(available)):
                item = types.InlineKeyboardButton(text=available[i][0], callback_data=f'test{available[i][1]}')
                markup_inline.add(item)
            bot.send_message(message.chat.id, 'Вам доступны следующие тесты:', reply_markup=markup_inline)
        else:
            bot.send_message(message.chat.id, 'Для Вас нет доступных тестов!')
    else:
        (bot.send_message(message.chat.id,
                          'Вы не авторизовались. Для просмотра доступных тестов пройдите авторизацию (/login)'))


@bot.callback_query_handler(func=lambda call: True)
def answer_test(call):
    if call.data.find('test') != -1:
        global cur_id_test
        cur_id_test = call.data[4:]
        markup_inline = types.InlineKeyboardMarkup()
        item = types.InlineKeyboardButton(text="Начать", callback_data='start_t')
        markup_inline.add(item)
        bot.send_message(call.message.chat.id, create_description_for_test(), reply_markup=markup_inline)
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == 'start_t':
        take_test(call.message)
    elif call.data.find('answer') != -1:
        take_button_answer(call.data)
    elif call.data == 'end1':
        save_all_answer(call.message)
    elif call.data == 'end2':
        get_number_edit_answer(call.message)
    bot.answer_callback_query(callback_query_id=call.id)


def create_description_for_test():
    buffer = DBHelper.get_description_for_test(cur_id_test)
    quantity_attempts = DBHelper.get_name_and_quantity_attempts_test(cur_id_test)
    print(quantity_attempts)
    if len(quantity_attempts) > 0:
        quantity_attempts = quantity_attempts[0][1]
    else:
        quantity_attempts = buffer[0][4]
    description = f"{buffer[0][1]}\n\nКоличество вопросов: {buffer[0][3]}\nКоличество попыток: {buffer[0][4]}\n" \
                  f"Количество оставшихся попыток: {quantity_attempts}\n\n" \
                  f"Описание:\n{buffer[0][2]}\n\nАвтор теста: {buffer[0][5]} "
    return description


def take_button_answer(data):
    print("data = " + data)
    global cur_answer
    global flag_get_answer
    flag_get_answer = True
    cur_answer = int(data[6:7])
    check = data.find('+')
    if check != -1:
        number = int(data[check + 1:])
        answers[number] = '+'
    print("answers = ", answers)


def save_all_answer(message):
    count_right_answers = answers.count('+')
    format_answer = []
    for i in range(0, len(answers)):
        format_answer.append(f'{i + 1}) {answers[i]}')
    format_answer = '\n'.join(format_answer)
    data_about_test = DBHelper.get_name_and_quantity_attempts_test(cur_id_test)
    bot.send_message(message.chat.id,
                     f"{data_about_test[0][0]}\nВаш результат: {count_right_answers} из {len(answers)} \n{format_answer}")
    mass = [cur_group_student, cur_id, int(count_right_answers), int(cur_id_test), int(data_about_test[0][1])]
    print(mass)
    DBHelper.set_result(cur_group_student, cur_id, int(count_right_answers), int(cur_id_test),
                        int(data_about_test[0][1]))


def get_number_edit_answer(message):
    number = bot.send_message(message.chat.id, 'Введите номер вопроса, в котором хотите изменить ответ')
    bot.register_next_step_handler(number, edit_answer)


def edit_answer(message):
    if len(answers) >= int(message.text) > 0:
        number_question = int(message.text) - 1
        buffer_question = DBHelper.get_one_question(cur_id_test, number_question)
        send_question(message, number_question, buffer_question)
        end_test(message)
    else:
        msg = bot.send_message(message.chat.id,
                               'Вы ввели некорректный номер вопроса! Введите корректный номер вопроса: ')
        edit_answer(msg)


def send_question(message, number_question, buffer_question):
    # buffer_question[0][0] - сам вопрос
    # buffer_question[n][1] - вариант ответа
    # buffer_question[n][2] - правильность варианта ответа
    markup_inline = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton(text=buffer_question[0][1],
                                       callback_data=f'answer1_{buffer_question[0][2]}{number_question}')
    item2 = types.InlineKeyboardButton(text=buffer_question[1][1],
                                       callback_data=f'answer2_{buffer_question[1][2]}{number_question}')
    item3 = types.InlineKeyboardButton(text=buffer_question[2][1],
                                       callback_data=f'answer3_{buffer_question[2][2]}{number_question}')
    markup_inline.add(item1)
    markup_inline.add(item2)
    markup_inline.add(item3)
    bot.send_message(message.chat.id, buffer_question[0][0],
                     reply_markup=markup_inline)
    global flag_get_answer
    while not flag_get_answer:
        # print(flag_get_answer)
        continue
    bot.send_message(message.chat.id,
                     f"ответ '{buffer_question[cur_answer - 1][1]}' сохранен")

    flag_get_answer = False


def take_test(message):
    global cur_id_test
    quantity = int(DBHelper.get_quantity_questions_test(cur_id_test)[0][0])
    init_answers(quantity)
    for i in range(0, quantity, 1):
        buffer_question = DBHelper.get_one_question(cur_id_test, i)
        # print(f'id_test = {qur_id_test},i = {i}')
        # print(buffer_question)
        # buffer_question[0][0] - сам вопрос
        # buffer_question[n][1] - вариант ответа
        # buffer_question[n][2] - правильность варианта ответа
        send_question(message, i, buffer_question)

    end_test(message)
    print("test passed")


def end_test(message):
    end_test_buttons = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton(text="Сохранить", callback_data='end1')
    but2 = types.InlineKeyboardButton(text="Изменить ответ", callback_data='end2')
    end_test_buttons.add(but1, but2)
    bot.send_message(message.chat.id, 'Вы ответили на все вопросы теста. Желаете сохранить ответы и узнать результат?',
                     reply_markup=end_test_buttons)


def init_answers(quantity):
    global answers
    for i in range(0, quantity, 1):
        answers.append('-')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
