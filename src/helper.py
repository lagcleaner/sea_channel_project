def time_str(time):
    return str(int((time + 520) // 60)).rjust(2, ' ') + ":" + str(int(time) % 60).rjust(2, '0')
