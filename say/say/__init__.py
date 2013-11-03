import subprocess


def say(sentence):
    subprocess.call(["say", sentence])