# import sqlite3
import psycopg2
import localData
import datetime


def connect_to_db():
    try:
        connection = psycopg2.connect(
            host=localData.host,
            user=localData.user,
            password=localData.password,
            database=localData.db_name
        )
        return connection
    except Exception as ex:
        print('[Error PostgreSQL] connect_to_DB()', ex)


def check_session(client_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f'SELECT * from session where id={client_id};')
            res = cursor.fetchall()
        if len(res) > 0:
            return True
        else:
            return False
    except Exception as ex:
        print('[Error PostgreSQL] check_session(id)', ex)
    finally:
        connection.close()


def update_session(session_id, name, client_id, authorized):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""UPDATE session SET id = {session_id}, name = '{name}', 
                client_id = {client_id}, authorized = {authorized} WHERE id = {session_id};""")
            connection.commit()
    except Exception as ex:
        print('[Error PostgreSQL] update_session(id, name, client_id, authorized)', ex)
    finally:
        connection.close()


def create_note_session(session_id, name, client_id, authorized):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""INSERT INTO session (id, name, client_id, authorized)
                 VALUES ({session_id}, '{name}', {client_id}, {authorized});""")
        connection.commit()
    except Exception as ex:
        print('[Error PostgreSQL] create_note_session(id, name, client_id, authorized)', ex)
    finally:
        connection.close()


def checking_group_availability(group):
    '''
    Check the availability of the group in the databases. \n
    :param group: number group (str)
    :return: True - if the group is found;
            False - if no group is found
    '''
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT * from groups where number_group='{group}';""")
            res = cursor.fetchall()
        if len(res) > 0:
            return True
        else:
            return False
    except Exception as ex:
        print('[Error PostgreSQL] check_group(group)', ex)
    finally:
        connection.close()


def get_possible_students(name, group):
    '''
    Checks if there is a client with the name "name" in group "group" and,
    if there is, returns a possible passwords and id students.\n
    :param name: client name
    :param group: client number group (str)
    :return: possible_passwords[]
    '''
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT password, s.id FROM students s LEFT JOIN groups g ON s.group_id = g.id
             WHERE g.number_group='{group}' AND s.name='{name}';""")
            res = cursor.fetchall()
            finish_result = []
            for cpl in res:
                for mass in cpl:
                    finish_result.append(mass)
        return finish_result
    except Exception as ex:
        print('[Error PostgreSQL] get_possible_passwords(name, group)', ex)
    finally:
        connection.close()


def get_name_and_id_available_test(number_group):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT tests.name, tests.id FROM tests LEFT JOIN tests_groups tg on tests.id = tg.tests_id
             LEFT JOIN groups g on g.id = tg.groups_id WHERE g.number_group = '{number_group}'""")
            res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
        return res
    except Exception as ex:
        print('[Error PostgreSQL] find_available_test(number_group)', ex)
    finally:
        connection.close()


def get_all_answers():
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT id, choices, flag_correct FROM questions""")
            res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
        return res
    except Exception as ex:
        print('[Error PostgreSQL] find_available_test(number_group)', ex)
    finally:
        connection.close()


def insert_questions_in_data_base(data_for_request):
    data_for_request = [(1, 'Как называется таблица умножения?', 1),
                        (2, 'Как называется наука о геометрических фигурах?', 1),
                        (3, 'Короче ли катет гипотенузы?', 1),
                        (4, 'Верно ли, что 5% от 100 будут равны 100% от 5?', 1),
                        (5, 'Сколько десятков в числе 555?', 1)]
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.executemany(f"""INSERT INTO questions (number_question, question, tests_id) VALUES (%s,%s,%s)""",
                               data_for_request)
            connection.commit()
            # res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
        # print(res)
    except Exception as ex:
        print('[Error PostgreSQL] insert_question_in_data_base(data_for_request)', ex)
    finally:
        connection.close()


def insert_answers_in_data_base():
    answers = [
        (1, "1) Таблица Пифагора", True), (1, "2) Таблица Геродота", False), (1, "3) Таблица Шульте", False),
        (2, "1) Философия", False), (2, "2) Астрономия", False), (2, "3) Геометрия", True),
        (3, "1) Да", True), (3, "2) Нет", False), (3, "3) Они равны", False),
        (4, "1) Нет", False), (4, "2) Да", True), (4, "3) Зависит от единиц измерения", False),
        (5, "1) 5 десятков", False), (5, "2) 55 десятков", True), (5, "3) 555 десятков", False)
    ]
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.executemany(f"""INSERT INTO answers (question_id, answer, flag_correct) VALUES (%s,%s,%s)""",
                               answers)
            connection.commit()
            # res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
        # print(res)
    except Exception as ex:
        print('[Error PostgreSQL] insert_answers_in_data_base()', ex)
    finally:
        connection.close()


def get_data_for_description_test(test_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT tests.name, tests.quantity_questions, 
            tests.quantity_attempts, tests.description, teachers.name  FROM tests 
            LEFT JOIN teachers ON tests.author_id = teachers.id WHERE tests.id = {int(test_id)} """)
            connection.commit()
            res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
            return res
    except Exception as ex:
        print('[Error PostgreSQL] insert_answers_in_data_base()', ex)
    finally:
        connection.close()


def get_all_questions(test_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT number_question, question FROM questions WHERE tests_id = {test_id} 
            ORDER BY number_question""")
            connection.commit()
            res = cursor.fetchall()
            # finish_result = []
            # for cpl in res:
            #     for mass in cpl:
            #         finish_result.append(mass)
            return res
    except Exception as ex:
        print('[Error PostgreSQL] insert_answers_in_data_base()', ex)
    finally:
        connection.close()


def get_all_answers(test_id):
    '''

    :param test_id:
    :return: [(number_question_for(int),
               answer(str),
               correct(bool)), ]
    '''
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT q.number_question, answer, flag_correct FROM answers a LEFT JOIN questions q on q.id = a.question_id
             WHERE tests_id = {test_id} ORDER BY number_question""")
            connection.commit()
            res = cursor.fetchall()
            return res
    except Exception as ex:
        print('[Error PostgreSQL] get_all_answers(test_id)\t', ex)
    finally:
        connection.close()
    # try:
    #     connection = connect_to_db()
    #     with connection.cursor() as cursor:
    #         cursor.execute(f"""SELECT number_question, question FROM questions WHERE tests_id = {test_id}
    #         ORDER BY number_question""")
    #         connection.commit()
    #         res = cursor.fetchall()
    #         return res
    # except Exception as ex:
    #     print('[Error PostgreSQL] insert_answers_in_data_base()', ex)
    # finally:
    #     connection.close()


def record_result(student_id, tests_id, result, date, remaining_attempts):
    if remaining_attempts < 0:
        print("[Error] record_result: remaining_attempts < 0")
        return
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""INSERT INTO results (students_id, tests_id, result, date, remaining_attempts)
                 VALUES ({student_id},{tests_id},{result},'{date}',{remaining_attempts})""")
        connection.commit()
    except Exception as ex:
        print('[Error PostgreSQL] record_result(student_id, tests_id, result, date)', ex)
    finally:
        connection.close()


def get_remaining_attempts_for_test(student_id, test_id):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT MIN(remaining_attempts) FROM results 
                WHERE tests_id = {test_id} AND students_id = {student_id}""")
            res = cursor.fetchall()
            if res[0][0] is None:
                print("none")
                cursor.execute(f"""SELECT quantity_attempts FROM tests WHERE id = {test_id}""")
                res = cursor.fetchall()
            return res[0][0]
    except Exception as ex:
        print('[Error PostgreSQL] get_remaining_attempts_for_test(student_id, test_id)', ex)
    finally:
        connection.close()


def get_one_question(test_id, number_question):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(
                f"""SELECT question FROM questions  WHERE tests_id = {test_id} AND number_question = {number_question}""")
            res = cursor.fetchall()
            return res
    except Exception as ex:
        print('[Error PostgreSQL] get_one_question(test_id, number_question)\t', ex)
    finally:
        connection.close()


def get_answers_for_one_question(test_id, number_question):
    try:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT q.number_question, answer, flag_correct FROM answers a LEFT JOIN questions q 
            on q.id = a.question_id WHERE tests_id = {test_id} AND number_question = {number_question}""")
            connection.commit()
            res = cursor.fetchall()
            return res
    except Exception as ex:
        print('[Error PostgreSQL] get_answers_for_one_question(test_id, number_question)\t', ex)
    finally:
        connection.close()


#
# # old methods
# # def find_available_test(number_group):
# #     base = sqlite3.connect('dataBase/DB_chat_test.db')
# #     cursor = base.cursor()
# #     res = cursor.execute('SELECT name_test, id FROM tests WHERE for_groups == ? ', (number_group,)).fetchall()
# #     base.close()
# #     return res
#
#
# def find_in_group(number_group):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute('SELECT name, id FROM students WHERE groups == ?', (number_group,)).fetchall()
#     base.close()
#     return res
#
#
# def find_id_student(number_group, name):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute('SELECT id FROM students WHERE groups == ? AND name == ?', (number_group, name)).fetchall()
#     base.close()
#     return res
#
#
# def get_description_for_test(id_test):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute('SELECT * FROM tests WHERE id == ? ', (id_test,)).fetchall()
#     base.close()
#     return res
#
#
# def get_quantity_questions_test(id_test):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute('SELECT quantity_question FROM tests WHERE id == ? ', (id_test,)).fetchall()
#     base.close()
#     return res
#
#
# def get_one_question(id_test, number_question):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute(
#         'SELECT question, choices, correct FROM questions WHERE id_test == ? AND number_question == ? ',
#         (id_test, number_question)).fetchall()
#     base.close()
#     return res
#
#
# def get_name_and_quantity_attempts_test(id_test):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute(
#         f'SELECT name_test, quantity_attempts FROM tests WHERE id == ? ', (id_test,)).fetchall()
#     base.close()
#     return res
#
#
# def set_result(number_group, id_student, result, id_test, all_attempts):
#     base = sqlite3.connect('dataBase/DB_chat_test.db')
#     cursor = base.cursor()
#     res = cursor.execute(
#         f'SELECT remaining_attempts FROM results WHERE id_student == {id_student} AND id_test == {id_test}').fetchall()
#     print(f'len(res) = {len(res)}')
#     if len(res) > 0:
#         r = cursor.execute(
#             f'UPDATE results SET result == {result}, remaining_attempts == {res[0][0] - 1} WHERE id_student == '
#             f'{str(id_student)} AND id_test == {id_test}').fetchall()
#         print(r)
#         print(f'UPDATE {id_student}')
#         base.commit()
#         base.close()
#     else:
#         print(f'INSERT {id_student}')
#         cursor.execute(
#             f'INSERT INTO results (number_groups, id_student, id_test, result, remaining_attempts, all_attempts ) '
#             f'VALUES ({number_group}, {str(id_student)}, {id_test}, '
#             f'{int(result)},{int(all_attempts - 1)}, {int(all_attempts)})')
#         base.commit()
#         res = cursor.execute('SELECT * FROM results').fetchall()
#         base.close()
#     return res


if __name__ == '__main__':
    # print(get_remaining_attempts_for_test(1, 1))
    # ra = get_remaining_attempts_for_test(1, 1)
    # dt = datetime.datetime.now()
    # record_result(1, 1, 5, dt, ra)




    def prepare_data_questions_for_request_sql(list_questions):
        result = []
        number_question = 1;
        for one_question in list_questions:
            result.append((number_question, one_question, 1))
            number_question += 1
        # print(result)


    questions = ['Как называется таблица умножения?',
                 'Как называется наука о геометрических фигурах?',
                 'Короче ли катет гипотенузы?',
                 'Верно ли, что 5% от 100 будут равны 100% от 5?',
                 'Сколько десятков в числе 555?']
    answers = [[["1) Таблица Пифагора", True], ["2) Таблица Геродота", False], ["3) Таблица Шульте", False]],
               [["1) Философия", False], ["2) Астрономия", False], ["3) Геометрия", True]],
               [["1) Да", True], ["2) Нет", False], ["3) Они равны", False]],
               [["1) Нет", False], ["2) Да", True], ["3) Зависит от единиц измерения", False]],
               [["1) 5 десятков", False], ["2) 55 десятков", True], ["3) 555 десятков", False]]]
