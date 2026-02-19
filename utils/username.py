import random
def create_username():
    username = "anonyuser_"
    for _ in range(4):
        username += str(random.randint(0, 9))
    return username