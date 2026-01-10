import subprocess
import time

print("Starting server...")
with open("server_log.txt", "w") as f:
    process = subprocess.Popen(["python", "run.py"], stdout=f, stderr=f)
    print("Waiting 5 seconds for startup...")
    time.sleep(5)
    print("Checking if still alive...")
    if process.poll() is None:
        print("Server is still running!")
        process.terminate()
    else:
        print("Server died.")
        with open("server_log.txt", "r") as log:
            print("Log content:")
            print(log.read())
