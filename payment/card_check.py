from wtforms import ValidationError
from datetime import datetime

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = 0
    checksum += sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d*2))
    return checksum % 10

def is_luhn_valid(form, field):
    if luhn_checksum(field) != 0:
        raise ValidationError("Invalid Card Number!")
    
def check_date(form, field):
    date = field.split("/")
    month = int(date[0])
    year = int(date[1])
    if month < datetime.month() and month > 12 and year < datetime.year():
        raise ValidationError("Invalid Date!")

