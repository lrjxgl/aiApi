import os
import time
def canTask():
    file_path="./task.lock"
    if os.path.exists(file_path):
        modified_time = os.path.getmtime(file_path)
        current_time = time.time()
        if current_time-modified_time>600:
            return True
        else:
            return False
    else:       
        return True
def addTask():
    file_path="./task.lock"
    with open(file_path, 'w') as file:
            file.write('')
def removeTask():
    file_path="./task.lock"
    if os.path.exists(file_path):
        os.remove(file_path)
        