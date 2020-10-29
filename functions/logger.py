import os
import time


def formatDatetime():
    t = time.localtime()
    t = list(t)
    i = 0
    datetime = ""

    for e in t:

        if len(str(e)) < 2:
            e = "0" + str(e)

        if i < 2:
            datetime += str(e)
            datetime += "-"
            i += 1
        elif i == 2:
            datetime += str(e)
            i += 1
        elif i == 3:
            datetime += " "
            datetime += str(e)
            i += 1
        elif i < 6 and i > 3:
            datetime += ":"
            datetime += str(e)
            i += 1
        else:
            break
    return(datetime)


def logtofile(path, level, message):
    file = open(path, "a")
    file.write("\n")
    file.write(formatDatetime())
    file.write(" ")
    file.write(level.upper())
    file.write(": ")
    file.write(message)
    file.close()
