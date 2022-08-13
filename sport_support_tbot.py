import time
from programs_storage import TxtStorage
from telebot import TeleBot


def run_bot_server(token):
    bot = TeleBot(token)

    storage_tool = TxtStorage()
    users_programs = storage_tool.storage  # dictionary {}

    @bot.message_handler(commands=['start', 'help'])
    def tbot_welcome_message(message):
        ''' Welcome new user '''
        bot.reply_to(
            message, "Hello! Write /set_program to create individual program.")

    @bot.message_handler(commands=['set_program'])
    def tbot_set_sport_program(message):
        ''' Create individual program '''
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

        if not message.chat.id in users_programs.keys():
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

    @bot.message_handler(commands=['program'])
    def tbot_start_sport_program(message):
        ''' Start individual program '''
        # check args
        if len(message.text) < 2:
            bot.reply_to(message, "Write /program <program's name>")
            return None
        pr_name = message.text.split(' ')[1]
        if pr_name not in users_programs[message.chat.id].keys():
            bot.reply_to(message, f"Program {pr_name} doesn't exist!")

        # starting program
        exercises = users_programs[message.chat.id][pr_name]
        counter = 0

        def _do_exercise(message):
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
        del storage_tool.storage


if __name__ == '__main__':
    run_bot_server('TOKEN')
