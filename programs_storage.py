from logger import logger

storage_filename = '_programs.data'  # direction for programs save

# format in main: { user: {program: [ (do, repeats, time) ] } }

# TODO: do with database SQL later


class StorageDescriptor:
    """ Descriptor for saving sport programs in text file """

    def __init__(self, filename: str):
        self.users_programs = {}
        self.filename = filename
        try:
            with open(self.filename, 'r') as fd:
                # read saved sport programs
                lines = fd.readlines()
                for line in lines:
                    user_data = line.split(' ')
                    self.users_programs[int(user_data[0])] = {}
                    for i in range(1, len(user_data)):
                        program_data = user_data[i].split(':')
                        program_name, exercises = program_data[0], program_data[1].split(
                            '|')
                        exercises = [ex.split(',') for ex in exercises]
                        del exercises[-1]
                        exercises = [(ex[0], ex[1], ex[2]) for ex in exercises]
                        self.users_programs[int(
                            user_data[0])][program_name] = exercises
        except FileNotFoundError:
            logger.error(
                f"File {storage_filename} doesn't exist. Nothing will be saved.")

    def __get__(self, instance, owner):
        return self.users_programs

    def __delete__(self, obj):
        with open(self.filename, 'w') as fd:
            # save sport programs
            for user, programs in self.users_programs.items():
                fd.write(str(user))
                for program, exercises in programs.items():
                    fd.write(' ')
                    fd.write(program + ':')
                    for ex in exercises:
                        fd.write(str(ex).replace(' ', '').replace('(', '')
                                 .replace(')', '|').replace("'", ''))
                fd.write('\n')

        del self


class TxtStorage:
    """ Saving sport programs in text file storage_filename """
    storage = StorageDescriptor(storage_filename)
