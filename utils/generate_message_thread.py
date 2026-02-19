import uuid

def generate_message_thread():
    return "whisperchat_" + str(uuid.uuid4())

def generate_room_thread():
    return "whisperroom_" + str(uuid.uuid4())