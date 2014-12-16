import datetime

def get_dow():
    dow = datetime.date.today().isoweekday()
    if dow == 7:
        dow = 0
    return dow
