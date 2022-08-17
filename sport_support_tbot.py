import time
from programs_storage import TxtStorage
from telebot import TeleBot


def run_bot_server(token):
    ''' Main process. Bot running '''
    bot = TeleBot(token)

    storage_tool = TxtStorage()
    users_programs = storage_tool.storage  # dictionary {}

    @bot.message_handler(commands=['start', 'help'])
    def tbot_welcome_message(message):
        ''' Welcome new user '''
        bot.reply_to(
            message, "Hello! Write /set_program to create individual program.")

    # @bot.message_handler(commands=['old_set_program'])
    def tbot_set_sport_program_old(message):
        ''' Create individual program. Old version '''
        exercises = [ex.split(' ') for ex in message.text.split('\n')]
        usage_msg = 'Use: /set_program <program_name>\n' + \
                    '<1st exercise name> <repeats> <timer in minutes>\n' + \
                    '<2nd exercise name> <repeats> <timer in minutes>\n' + \
                    '...\n' + \
                    '<nnd exercise name> <repeats> <timer in minutes>\n' + \
                    'P.S. to off repeats or timer write "-" in that section\n'
        if len(exercises) < 2:
            bot.reply_to(message,
                         usage_msg)
            return None
        for ex in exercises:
            if len(ex) == 2 and ex[0] == '/set_program':
                # command with program_name is ok
                continue
            elif len(ex) < 3:
                # wrong format for program setting
                bot.reply_to(message, usage_msg)
                return None

        if message.chat.id not in users_programs.keys():
            users_programs[message.chat.id] = {}
        users_programs[message.chat.id][exercises[0][1]] = \
            [(exercises[i][0],
              exercises[i][1],
              exercises[i][2])
             for i in range(1, len(exercises))]

        bot.reply_to(message,
                     f"Program {exercises[0][1]} has created.\n" +
                     f'''Use "/program {exercises[0][1]}" ''' +
                     "to this personal program.")

    @bot.message_handler(commands=['set_program'])
    def tbot_set_sport_program(message):
        ''' Create individual program '''
        exercises = []  # list for fulling
        counter = 1  # counter of exercises
        program_name = None

        def _get_program_name_step(message):
            ''' Get program_name and go to the exercise-parsing '''
            if message.chat.id not in users_programs.keys():
                users_programs[message.chat.id] = {}
            nonlocal program_name, counter
            program_name = message.text
            users_programs[message.chat.id][message.text] = []
            bot.send_message(message.chat.id,
                             f'Add the {counter}. exercise by sending a message like\n\n' +
                             'NAME REPEATS MINUTES\n\n' +
                             'Example: push-ups 10 2 (that means "Do push-ups 10 times for 2 minutes)".\n' +
                             'To skip useless option type "-" instead.')
            bot.register_next_step_handler(
                message, _get_exercise_step)

        def _get_exercise_step(message):
            ''' Get exercises step by step recursively '''
            nonlocal program_name, counter
            if counter > 1 and message.text == 'Done':
                # stop recursive creation of the program
                msg = f'Program {program_name}:\n\n'
                for ex in users_programs[message.chat.id][program_name]:
                    msg += f'{ex[0]}: {ex[1]} times for {ex[2]} minutes.\n'
                bot.send_message(message.chat.id, msg)
                return

            exercise = message.text.split()
            try:
                if exercise[1] != '-':
                    int(exercise[1])
                if exercise[2] != '-':
                    int(exercise[2])
                if len(exercise) < 3:
                    raise ValueError
            except (ValueError, IndexError):
                # wrong format of requested message
                bot.send_message(message.chat.id,
                                 'Usage:\n\n' +
                                 'NAME REPEATS MINUTES\n\n' +
                                 'Example: push-ups 10 2 (that means "Do push-ups 10 times for 2 minutes)".')
                bot.register_next_step_handler(
                    message, _get_exercise_step)
                return
            # adding exercise to the program
            users_programs[message.chat.id][program_name].append(
                (exercise[0], exercise[1], exercise[2]))
            counter += 1
            # going to the next exercise
            bot.send_message(message.chat.id,
                             f'Add the {counter}. exercise by sending a message like\n\n' +
                             'NAME REPEATS MINUTES\n\n' +
                             'Example: push-ups 10 2 (that means "Do push-ups 10 times for 2 minutes)".\n' +
                             'To skip useless option type "-" instead.\n' +
                             'To stop creating a program send "Done".')
            bot.register_next_step_handler(
                message, _get_exercise_step)

        bot.reply_to(message, "What is the name of your program?")
        bot.register_next_step_handler(message, _get_program_name_step)

    @bot.message_handler(commands=['program'])
    def tbot_start_sport_program(message):
        ''' Start individual program '''

        def __get_program_name(message):
            ''' Get name of program for "/program program_name" '''
            # start program
            message.text = '/program' + message.text
            tbot_set_sport_program(message)

        # check args
        if len(message.text.split(' ')) < 2:
            # need /program program_name format
            bot.reply_to(
                message, "What is the name of the program you want to start?")
            bot.register_next_step_handler(message, __get_program_name)
            bot.reply_to(message, "Write /program <program's name>")
            return None
        pr_name = message.text.split(' ')[1]
        if pr_name not in users_programs[message.chat.id].keys():
            bot.reply_to(message, f"Program {pr_name} doesn't exist!")
            return None

        # starting program
        exercises = users_programs[message.chat.id][pr_name]
        counter = 0

        def _do_exercise(message):
            ''' Do exercises recursively '''
            nonlocal counter, exercises

            ex = exercises[counter]
            msg = f'Do {ex[0]}'
            if ex[1] != '-':
                # repeats argument exists
                try:
                    ex_repeats = int(ex[1])
                    msg += f' {ex_repeats} times'
                except TypeError:
                    pass

            ex_timer = 0
            if ex[2] != '-':
                # timer argument exists
                try:
                    ex_timer = int(ex[2]) * 60  # minuntes
                    msg += f' for {int(ex_timer / 60)} minutes'
                except TypeError:
                    ex_timer = 0

            bot.send_message(message.chat.id, msg + '.')
            if ex_timer > 0:
                time.sleep(ex_timer)
                bot.send_message(message.chat.id, f'Time for {ex[0]} is over!')

            counter += 1
            if counter >= len(exercises):
                # program is over
                bot.send_message(
                    message.chat.id, f'The program is over! Good job.')
            else:
                # recursive continue
                bot.send_message(message.chat.id,
                                 'Send something to move on to the next exercise.')
                bot.register_next_step_handler(message, _do_exercise)

        _do_exercise(message)

    # polling start
    try:
        bot.infinity_polling()
    finally:
        # saving storage to the file
        del storage_tool.storage


if __name__ == '__main__':
    run_bot_server('TOKEN')
