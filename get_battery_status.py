import subprocess

def get_battery_status():
    result = subprocess.run(
        ['echo', 'get battery'],
        capture_output=True,
        text=True
    )
    # Pipe the output to nc
    nc = subprocess.run(
        ['nc', '-q', '0', '127.0.0.1', '8423'],
        input=result.stdout,
        capture_output=True,
        text=True
    )
    print(nc.stdout)

if __name__ == "__main__":
    get_battery_status() 