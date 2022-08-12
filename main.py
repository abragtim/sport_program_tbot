from typing import Type
from telebot import TeleBot


def main(token):
    bot = TeleBot(token)
    # TODO: do with SQL db
    users_programs = {}


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
        if pr_name not in users_programs[message.chat.id]:
            bot.reply_to(message, f"Program {pr_name} doesn't exist!")

        # starting program
        for ex in users_programs[message.chat.id][pr_name]:
            msg = f'Do {ex[0]} '
            if ex[1] != '-':
                # repeats argument exists
                try:
                    ex_repeats = int(ex[1])
                    msg += f'{ex_repeats} times '
                except TypeError:
                    pass
            if ex[2] != '-':
                # timer argument exists
                try:
                    ex_timer = int(ex[2])
                    # TODO: timer msg
                except TypeError:
                    pass
            bot.send_message(message.chat.id, msg)


    bot.infinity_polling()


if __name__ == '__main__':
    main('')
