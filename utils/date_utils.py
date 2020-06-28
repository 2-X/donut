import datetime


def make_datetime(year, month, day, hour=0, minute=0, second=0):
    return datetime.datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second
    )


def between_the_hours_of(hour1, hour2):
    """ is the current time between the hours of `hour1` and `hour2`?
    if hour2 is less than our equal to hour1, it is assumed
    that hour2 refers to some time the next day:
    (e.g.
        between_the_hours_of(7, 8) => between the hours of 7am today and 8am today
        between_the_hours_of(7, 7) => between the hours of 7am today and 7am tomorrow
        between_the_hours_of(7, 0) => between the hours of 7am today and 12am tomorrow (midnight)
    ) """
    now = datetime.datetime.now()
    hour1_dt = make_datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=hour1,
    )
    hour2_dt = make_datetime(
        year=now.year,
        month=now.month,
        day=now.day,
        hour=hour2,
    ) + datetime.timedelta(days=(1 if hour2 <= hour1 else 0))
    return (hour1_dt < now and now < hour2_dt)


def get_day_of_week(dt):
    days = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    return days[dt.weekday()]


def days_since(dt, as_dates=True):
    """ how many days between the given dates?
    if 'as_dates' is true, then it just ignores the
    time of day on the given date and today and just returns
    the difference between the dates """
    if as_dates:
        dt = datetime.datetime(
            year=dt.year,
            month=dt.month,
            day=dt.day
        )
    
    # get today's date
    today = datetime.datetime.today()
    if as_dates:
        today = datetime.datetime(
            year=today.year,
            month=today.month,
            day=today.day
        )

    # calculate days since that day
    days_since = (dt - today).days
    
    # else return days until
    return -1 * days_since