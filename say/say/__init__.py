import subprocess
import datetime
import bluetooth

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
    if se_puede_hablar():
        subprocess.call(["say", "-a", "38", sentence])
    else:
        print "como no se puede hablar el ", datetime.date.today(), " a las ", datetime.datetime.now().time(), "..."
        print "susurro: ", sentence