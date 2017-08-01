
number_of_days = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
   10: 31,
   11: 30,
   12: 31
}

def get_spending_track(amount, limit, month):
    spent_ratio = float(amount) / float(limit)
    days = number_of_days[month]
    # round up by adding one
    return int(days * spent_ratio) + 1
    
