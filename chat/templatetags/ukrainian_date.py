from django import template

register = template.Library()

MONTHS = {
    1: "січня",
    2: "лютого",
    3: "березня",
    4: "квітня",
    5: "травня",
    6: "червня",
    7: "липня",
    8: "серпня",
    9: "вересня",
    10: "жовтня",
    11: "листопада",
    12: "грудня",
}

@register.filter
def ua_date(value):
    try:
        day = value.day
        month = MONTHS[value.month]
        return f"{day} {month}"
    except:
        return value
