from io_tools.annotations.MOTParser import MOTParser


class ParserFactory:

    @staticmethod
    def get_parser(filePath: str):
        with open(filePath) as file:
            line = file.readline()
            if line[0] == '<':
                print("is XML")
            elif line[0] == '{':
                print("is JSON")
            else:
                return MOTParser(filePath)
