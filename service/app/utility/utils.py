import math


def round_up_to_second_decimal(number):
    return math.ceil(number * 100) / 100


def truncate_to_second_decimal(number):
    return math.floor(number * 100) / 100
