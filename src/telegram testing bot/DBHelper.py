import sqlite3


def find_in_group(number_group):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute('SELECT name, id FROM students WHERE groups == ?', (number_group,)).fetchall()
    base.close()
    return res


def find_id_student(number_group, name):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute('SELECT id FROM students WHERE groups == ? AND name == ?', (number_group, name)).fetchall()
    base.close()
    return res


def find_available_test(number_group):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute('SELECT name_test, id FROM tests WHERE for_groups == ? ', (number_group,)).fetchall()
    base.close()
    return res


def get_description_for_test(id_test):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute('SELECT * FROM tests WHERE id == ? ', (id_test,)).fetchall()
    base.close()
    return res


def get_quantity_questions_test(id_test):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute('SELECT quantity_question FROM tests WHERE id == ? ', (id_test,)).fetchall()
    base.close()
    return res


def get_one_question(id_test, number_question):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute(
        'SELECT question, choices, correct FROM questions WHERE id_test == ? AND number_question == ? ',
        (id_test, number_question)).fetchall()
    base.close()
    return res



def get_name_and_quantity_attempts_test(id_test):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute(
        f'SELECT name_test, quantity_attempts FROM tests WHERE id == ? ', (id_test,)).fetchall()
    base.close()
    return res


def set_result(number_group, id_student, result, id_test, all_attempts):
    base = sqlite3.connect('../../dataBase/DB_chat_test.db')
    cursor = base.cursor()
    res = cursor.execute(
        f'SELECT remaining_attempts FROM results WHERE id_student == {id_student} AND id_test == {id_test}').fetchall()
    print(f'len(res) = {len(res)}')
    if len(res) > 0:
        r = cursor.execute(
            f'UPDATE results SET result == {result}, remaining_attempts == {res[0][0] - 1} WHERE id_student == {str(id_student)} AND id_test == {id_test}').fetchall()
        print(r)
        print(f'UPDATE {id_student}')
        base.commit()
        base.close()
    else:
        print(f'INSERT {id_student}')
        cursor.execute(
            f'INSERT INTO results (number_groups, id_student, id_test, result, remaining_attempts, all_attempts ) '
            f'VALUES ({number_group}, {str(id_student)}, {id_test}, {int(result)},{int(all_attempts - 1)}, {int(all_attempts)})')
        base.commit()
        res = cursor.execute('SELECT * FROM results').fetchall()
        base.close()
    return res


# # res = get_name_and_quantity_attempts_test('1')
# res = set_result('3932', '00051', 5, 1, 5)
# print(res)

# mass = ['-', '-', '+', '-', '-']
# str = ''
# str = mass
#
# print('\n'.join(mass))
