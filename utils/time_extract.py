from datetime import datetime

def extract_time(entered_time:datetime):
    time = entered_time.strftime("%d/%m/%y %I:%M %p")
    return time