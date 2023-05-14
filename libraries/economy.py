from . import user

def get_balance(uid: str) -> float:
    '''get the balance of a user'''
    result = user.get_data_by_uid(uid, 'balance')
    if result == '':
        return 0.0
    return float(result)

def set_balance(uid: str, balance: float):
    '''set the balance of a user'''
    user.set_data(uid, 'balance', str(balance))

def pay(uid: str, amount: float) -> bool:
    '''pay from a user'''
    if get_balance(uid) < amount:
        return False
    set_balance(uid, get_balance(uid) - amount)
    return True

def earn(uid: str, amount: float):
    '''earn from a user'''
    set_balance(uid, get_balance(uid) + amount)

def transfer(from_uid: str, to_uid: str, amount: float) -> bool:
    '''transfer from a user to another'''
    if not pay(from_uid, amount):
        return False
    earn(to_uid, amount)
    return True
