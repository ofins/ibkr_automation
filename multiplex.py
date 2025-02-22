import multiprocessing
import os
import time


def instance_worker(instance_id, command):
    """Worker function for each instance"""
    print(
        f"Instance {instance_id} (PID: {os.getpid()}) starting with command: {command}"
    )

    # Here you can implement what each instance should do
    # For demonstration, we'll just simulate some work
    for i in range(5):
        print(f"Instance {instance_id}: Working on step {i}...")
        time.sleep(1)
    print(f"Instance {instance_id} completed")


def run_instances(commands):
    """
    Run 4 instances using multiprocessing

    Args:
        commands: List of command strings or parameters
    """
    processes = []

    try:
        # Start 4 processes
        for i, cmd in enumerate(commands, 1):
            p = multiprocessing.Process(target=instance_worker, args=(i, cmd))
            processes.append(p)
            p.start()
            print(f"Started instance {i} with PID {p.pid}")

        # Wait for all processes to complete
        for p in processes:
            p.join()

        print("All instances completed")

    except KeyboardInterrupt:
        print("\nTerminating all instances...")
        for p in processes:
            p.terminate()
        raise


def main():
    # Define custom commands/parameters for each instance
    commands = [
        "python main.py --symbol 'AAPL'",
        "python main.py --symbol 'META'",
        "python main.py --symbol 'AMD'",
        "python main.py --symbol 'MU'",
    ]

    if len(commands) != 4:
        raise ValueError("Please specify exactly 4 commands")

    run_instances(commands)


if __name__ == "__main__":
    main()
