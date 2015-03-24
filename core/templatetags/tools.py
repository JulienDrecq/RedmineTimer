from django import template
from datetime import date, datetime, timedelta
register = template.Library()


def get_week_days_range(year, week):
    d = date(year, 1, 1)
    # Gestion du Vendredi, Samedi, Dimanche tombant un 1er Janvier
    # http://en.wikipedia.org/wiki/Week
    if d.weekday() > 3:
        d = d + timedelta(7 - d.weekday())
    else:
        d = d - timedelta(d.weekday())
    dlt = timedelta(days=(week - 1) * 7)
    return d + dlt, d + dlt + timedelta(days=6)


@register.filter
def display_format_time(time):
    result = u""
    if time == 0:
        return 0
    m, s = divmod(time * 60.0 * 60.0, 60)
    h, m = divmod(m, 60)
    if h != 0:
        result += u"%dh" % h
    if m != 0:
        result += u"%dmin" % m
    if s != 0:
        result += u"%dsec" % s
    return result