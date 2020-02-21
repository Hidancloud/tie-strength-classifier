import dates
from matplotlib import pyplot as plt
import numpy as np

seconds_in_month = 2628000
id1 = "213299754"
id2 = "175773664"
id3 = "118216952"


def distribution(t):
    return t


def heuristics(seconds):
    # written in a row messages,
    # messages with large content
    # just simple posts or memeses and etc.
    new_seconds = seconds
    return new_seconds


def build_with_xtime(abs_time, diffs, time_window=seconds_in_month):
    """
    Builds average frequency for sliding windows with size time_window and returns
    this frequencies as an array
    :param abs_time: time of messages
    :param time_window: in seconds
    :return: frequency array
    """
    answer = []
    abs_time = np.array(abs_time, dtype=np.int64)
    last = 0
    summ = np.int64(0)

    # first window iteration
    while (summ < time_window) and (last < (len(abs_time) - 1)):
        last += 1
        summ += abs_time[last - 1] - abs_time[last]
    summ -= abs_time[last - 1] - abs_time[last]
    answer.append(last / time_window)
    first = abs_time[0] - abs_time[1]

    # dynamically window updating
    for index in range(1, len(abs_time) - 1):
        last -= 1
        summ -= first
        first = abs_time[index] - abs_time[index + 1]
        while (summ < time_window) and (last < (len(abs_time) - 1)):
            last += 1
            summ += abs_time[last-1] - abs_time[last]
        summ -= abs_time[last - 1] - abs_time[last]
        answer.append((last - index)/time_window)

    # last window iteration
    last -= 1
    summ -= first
    while (summ < time_window) and (last < (len(abs_time) - 1)):
        last += 1
        summ += abs_time[last - 1] - abs_time[last]
    summ -= abs_time[last - 1] - abs_time[last]
    answer.append((last - len(abs_time) + 1) / time_window)

    answer.reverse()  # we might need it
    y = answer.copy()
    x = np.array(abs_time)
    x = (x - x[-1]) / time_window
    x = x[::-1]
    x = [t for t in x if t < (x[-1] - 1)]
    y = [y[i] for i in range(len(x))]
    return x, y


def build_with_xmsg(time, differences, window_size=3000):
    ans = [window_size/sum(differences[x:x+window_size]) for x in range(0, len(differences)-window_size)]
    ans.reverse()
    return ans


def plot_dist_xtime(identifier="213299754", window_size=seconds_in_month):
    """
    :param identifier: id of user
    :param model: method for calculating frequency
    :param window_size: in seconds or number of messages
    :return: nothing
    """
    dates.create_single_file(identifier)
    plt.figure(figsize=(10, 7.), dpi=300)
    diffs, timing = dates.making_difference_sorted(dates.get_directed_dates(identifier, from_me=True))
    ans = build_with_xtime(timing, diffs, window_size)  # window_size is seconds only for xtime
    x_user1 = np.array(ans[0])
    y_user1 = np.array(ans[1])
    plt.plot(x_user1, y_user1, label="User1 activity", lw=3.5)

    diffs, timing = dates.making_difference_sorted(dates.get_directed_dates(identifier, from_me=False))
    ans = build_with_xtime(timing, diffs, window_size)  # window_size is seconds only for xtime
    x_user2 = np.array(ans[0])
    y_user2 = np.array(ans[1])
    plt.plot(x_user2, y_user2, label="User2 activity", lw=3.5)

    diffs, timing = dates.making_difference_sorted(dates.get_dates(identifier))
    ans = build_with_xtime(timing, diffs, window_size)  # window_size is seconds only for xtime
    plt.plot(ans[0], ans[1], label="Summary activity", lw=3.5)

    plt.legend()
    plt.xlabel("months", fontsize=27)
    plt.ylabel("frequency", fontsize=27)
    plt.show()

    plt.figure(figsize=(10, 7.), dpi=300)
    y = np.interp(x_user2, x_user1, y_user1) - y_user2
    plt.plot(x_user2, y, label="difference in activity", lw=3.5)
    plt.xlabel("months", fontsize=27)
    plt.ylabel("difference", fontsize=27)
    #print("vk.com/id{id} игнорит {count} сообщений в месяц".format(id=identifier, count=np.mean(y)*window_size))
    print("\n\n\n")
    plt.show()


def testing_timing(time):
    xx = time.copy()
    xx.reverse()
    yy = list(range(len(time)))
    plt.plot(xx, yy)
    plt.show()


plot_dist_xtime(identifier=id1, window_size=seconds_in_month)
plot_dist_xtime(identifier=id2, window_size=seconds_in_month)
# plot_dist_xtime(identifier=id3, window_size=seconds_in_month/30)

# todo:
#  3) think about heuristics for messages-in-a-row
#  4) optional: remove all inverses and do inverse in timing method in dates.py
#  6) optional: if file exists read it instead of making in dates.py
