import re


def email_phone(d):
    re_phone = re.compile(r'^\+?1?\d{9,15}$')
    re_email = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    data = {
        'email': '',
        'phone_number': '',
        'email_phone': 'Invalid email or phone number.'
    }
    if re_phone.match(d):
        data['phone_number'] = d
    elif re_email.match(d):
        data['email'] = d
    else:
        data['data'] = 'Invalid email or phone number.'
    return data
