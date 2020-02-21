import os
import re
import datetime as dt
from bs4 import BeautifulSoup
import lxml
from codecs import open

"""
These methods are used for getting data from vk.com and process it
in order to work with it later on
"""

months = {'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'мая': 5, 'июн': 6, 'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10,
          'ноя': 11, 'дек': 12}


def date_converter(date):
    """
    converts date from string format to the number of seconds passed since 1.1.1 0:0:0
    :param date: date to convert
    :return: the number of seconds passed since 1.1.1 0:0:0
    """
    splitted = date.split(' ')
    day, month, year, t = int(splitted[0]), months[splitted[1]], int(splitted[2]), splitted[4].split(':')
    hour, minute, second = int(t[0]), int(t[1]), int(t[2])
    return int(dt.datetime(year, month, day, hour, minute, second).timestamp())


def get_dates(c_id):
    """
    collects data from the dataset
    :param c_id: id of the user
    :return: dates of messages in form of string
    """
    messages = open(os.getcwd() + '/data/raw/' + c_id + '_messages.txt', 'r', encoding='windows-1251').read()
    message_time = open(os.getcwd() + "/data/preprocessed/" + c_id + "_time.txt", "w")
    date_mask = r'\d+ [а-я]{3} 20[0-9]{2} в \d+:\d\d:\d\d'
    mask = r'<div class="message__header">.*</div>'
    answer = re.findall(mask, messages)
    messaging = []
    for message in answer:
        ans = re.search(date_mask, message)
        message_time.write(ans.group(0) + "\n")
        messaging.append(ans.group(0))
    message_time.close()
    return messaging


def get_directed_dates(c_id="164952497", from_me=True):
    messages = open(os.getcwd() + '/data/raw/' + c_id + '_messages.txt', 'r', encoding='windows-1251').read()
    message_time = open(os.getcwd() + "/data/preprocessed/" + c_id + "_" + str(from_me) + "_time.txt", "w")
    date_mask = r'\d+ [а-я]{3} 20[0-9]{2} в \d+:\d\d:\d\d'
    if from_me:
        mask = r'<div class="message__header">Вы, .*</div>'
    else:
        mask = r'<div class="message__header"><a href="https://vk.com/id{id}">.*</div>'.format(id=c_id)
    answer = re.findall(mask, messages)
    messaging = []
    for message in answer:
        ans = re.search(date_mask, message)
        message_time.write(ans.group(0) + "\n")
        messaging.append(ans.group(0))
    message_time.close()
    return messaging


def slow_get_directed_dates(c_id="164952497", from_me=True):  
    messages = open(os.getcwd() + '/data/raw/' + c_id + '_messages.txt', 'r', encoding='windows-1251').read()
    message_time = open(os.getcwd() + "/data/preprocessed/" + c_id + "_" + str(from_me) + "_time.txt", "w")
    soup = BeautifulSoup(messages, "lxml")
    soup.prettify()
    soup = soup.find_all("div", {"class": "message__header"})
    answer = []
    if from_me:
        for element in soup:
            if element.a is None:
                answer.append(element.text.split(",")[1][1:23])
                message_time.write(answer[-1] + "\n")
    else:
        for element in soup:
            if element.a is not None:
                answer.append(element.text.split(",")[1][1:23])
                message_time.write(answer[-1] + "\n")
    message_time.close()
    return answer


def create_single_file(id):
    """
    We have lots of files, this feature writes them into one
    :param id: id of user
    :return: nothing, just creates a file
    """
    path = os.getcwd() + '/data/raw/'
    filenames = [path + id + '/' + x for x in os.listdir(path + id)]
    with open(path + id + '_messages.txt', 'wb') as outfile:
        for fname in filenames:
            with open(fname, "rb") as infile:
                # resulting file will be in windows-1251 encoding
                outfile.write(infile.read()[23:-8])
    outfile.close()


def day_night(time):
    """
    way to know the night period for the date in seconds format
    :param time: date we are interested in
    :return: night and day on this date in seconds
    """
    copy_night = time[1].split(' ')[:-1]
    copy_night.append('23:00:00')
    copy_night = " ".join(copy_night)
    copy_day = time[1].split(' ')[:-1]
    copy_day.append('11:00:00')
    copy_day = " ".join(copy_day)
    return date_converter(copy_night), date_converter(copy_day)


def making_difference_sorted(ttime, hours=3):
    time = []
    for i in ttime:
        # for working with daynight (String -> daynight OK, number -> daynight NOT OK)
        time.append([date_converter(i), i])
    # [[50, 1.1.1 0:0:50], ...]
    time = sorted(time, key=lambda x: x[0], reverse=True)
    for i in range(len(time) - 1):
        time[i][0] = time[i][0] - time[i + 1][0]
        # handling night periods without messaging
        night, day = day_night(time[i])
        daytime = date_converter(time[i][1])
        if time[i][0] > 3600*hours and day >= daytime >= night:
            if i > 1:
                time[i][0] = time[i-1][0]
            else:
                time[i][0] = 0
    time[-1][0] = 0
    return [x[0] for x in time], [date_converter(y[1]) for y in time]
