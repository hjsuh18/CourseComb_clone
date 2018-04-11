def time_compare(x, y):
    if x.hour < y.hour:
        return 1
    elif x.hour > y.hour:
        return -1
    if x.minute < y.minute:
        return 1
    elif x.minute > y.minute:
        return -1
    return 0

# convert days of the week string representation to array
def day_convert(day):
    day_array = [0, 0, 0, 0, 0]
    for i in range(0, len(day)):
        d = day[i]
        if d == 'M':
            day_array[0] = 1
        if d == 'T':
            if i + 1 < len(day) and day[i + 1] == 'h':
                day_array[3] = 1
                i += 1
            else:
                day_array[1] = 1
        if d == 'W':
            day_array[2] = 1
        if d == 'F':
            day_array[4] = 1
    return day_array

# return a list of days where x and y overlap
def day_compare(x, y):
    day_1 = day_convert(x)
    day_2 = day_convert(y)
    for i in range (0, 5):
        if day_1[i] + day_2[i] == 2:
            return True
    return False