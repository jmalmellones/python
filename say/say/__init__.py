import subprocess
import datetime
import sys

week_day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
weekend = ['Saturday', 'Sunday']


def se_puede_hablar():
    now = datetime.datetime.now().time()
    today = datetime.date.today()

    if today.strftime("%A") in week_day and datetime.time(18) < now < datetime.time(23):
        return True
    if today.strftime("%A") in weekend and datetime.time(11) < now < datetime.time(23):
        return True
    return False


def say(sentence):
    if sys.platform == "darwin":
        # only if we are in a Mac
        if se_puede_hablar():
            subprocess.call(["say", "-a", "38", sentence])
            return
    print "say: ", sentence