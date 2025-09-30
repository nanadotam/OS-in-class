import simpy
import tkinter as tk
# applying a queue for waiting jobs
from queue import Queue
from colorama import init, Fore, Style

# initialize colorama
init(autoreset=True)

'''
This program is to simulate inserting jobs into memory blocks in a fixed partition interface.
'''

# Job List
jobs = [
    {'stream': 1, 'time': 5, 'size': 5760},
    {'stream': 2, 'time': 4, 'size': 4190},
    {'stream': 3, 'time': 8, 'size': 3290},
    {'stream': 4, 'time': 2, 'size': 2030},
    {'stream': 5, 'time': 2, 'size': 2550},
    {'stream': 6, 'time': 6, 'size': 6990},
    {'stream': 7, 'time': 8, 'size': 8940},
    {'stream': 8, 'time': 10, 'size': 740},
    {'stream': 9, 'time': 7, 'size': 3930},
    {'stream': 10, 'time': 6, 'size': 6890},
    {'stream': 11, 'time': 5, 'size': 6580},
    {'stream': 12, 'time': 8, 'size': 3820},
    {'stream': 13, 'time': 9, 'size': 9140},
    {'stream': 14, 'time': 10, 'size': 420},
    {'stream': 15, 'time': 10, 'size': 220},
    {'stream': 16, 'time': 7, 'size': 7540},
    {'stream': 17, 'time': 3, 'size': 3210},
    {'stream': 18, 'time': 1, 'size': 1380},
    {'stream': 19, 'time': 9, 'size': 9850},
    {'stream': 20, 'time': 3, 'size': 3610},
    {'stream': 21, 'time': 7, 'size': 7540},
    {'stream': 22, 'time': 2, 'size': 2710},
    {'stream': 23, 'time': 8, 'size': 8390},
    {'stream': 24, 'time': 5, 'size': 5950},
    {'stream': 25, 'time': 10, 'size': 760},
]

# Improve memory list by adding a status to each block
memory = [
    {'block': 1, 'size': 9500, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 2, 'size': 7000, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 3, 'size': 4500, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 4, 'size': 8500, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 5, 'size': 3000, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 6, 'size': 9000, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 7, 'size': 1000, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 8, 'size': 5500, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 9, 'size': 1500, 'status': 'free', 'job': None, 'internal_fragmentation': 0},
    {'block': 10, 'size': 500, 'status': 'free', 'job': None, 'internal_fragmentation': 0}
]


# global waiting queue
waiting_jobs = Queue()

# Define functions

def first_fit(job, memory):
    # 1. check the memory status to see if there is any available memory block that can fit the job size.
    for block in memory:
        if block['status'] == 'free' and block['size'] >= job['size']:
            allocate_memory(job, block)
            return block
        
    print(Fore.RED + f"Job {job['stream']} of size {job['size']} cannot be allocated.")
    return None


def best_fit(job, memory):
    #  sort the memory block in ascending order based on their sizes.
    for block in sorted(memory, key=lambda x: x['size']):
        if block['status'] == 'free' and block['size'] >= job['size']:
            allocate_memory(job, block)
            return block

    print(Fore.RED + f"Job {job['stream']} of size {job['size']} cannot be allocated.")
    return None
   

def allocate_memory(job, block):
    # assign the job
    block['status'] = 'occupied'
    block['job'] = job
    size_wasted = block['size'] - job['size']
    block['internal_fragmentation'] = size_wasted
    print(Fore.GREEN + f"Job {job['stream']} allocated to Block {block['block']} (waste={size_wasted}).")


def deallocate_memory(block):
    # free space in memory 
    finished_job = block['job']
    block['status'] = 'free'
    block['job'] = None
    block['internal_fragmentation'] = 0
    print(Fore.CYAN + f"Job {finished_job['stream']} finished. Block {block['block']} is now free.")
    free_waiting_queue(memory)


# waiting queue function
# FIFO
def waiting_queue(job):
    """
    Jobs that cant go in memory go here
    """
    print(Fore.YELLOW + f"Job {job['stream']} of size {job['size']} added to waiting queue.")
    waiting_jobs.put(job)


def free_waiting_queue(memory):
    """
    Frees up the waiting queue after a job has been entered
    """
    if waiting_jobs.empty():
        return
    
    queue_length = waiting_jobs.qsize()
    for _ in range(waiting_jobs.qsize()):
        job = waiting_jobs.get()

        for block in memory:
            if block['status'] == 'free' and block['size'] >= job['size']:
                allocate_memory(job, block)
                print(Fore.MAGENTA + f"Job {job['stream']} allocated from waiting queue to block {block['block']}.")
                break   

        else:
            waiting_jobs.put(job)
            print(Fore.RED + f"Job {job['stream']} remains in waiting queue.")
            break


def job_process(env, job, memory, strategy="first_fit"):
    if strategy == "first_fit":
        b = first_fit(job, memory)
    else:
        b = best_fit(job, memory)

    if b is None:
        waiting_queue(job)
    else:
        yield env.timeout(job['stream'])
        deallocate_memory(b)


# --------------------------
# CLI Menu
# --------------------------

def print_memory():
    print("\n=== Memory Status ===")
    for block in memory:
        color = Fore.GREEN if block['status'] == 'free' else Fore.RED
        print(color + f"Block {block['block']}: {block['status']} | size={block['size']} | job={block['job']} | waste={block['internal_fragmentation']}")
    print("=====================\n")


def run_simulation(strategy):
    env = simpy.Environment()
    for job in jobs:
        env.process(job_process(env, job, memory, strategy))
    env.run()
    print(Fore.CYAN + "Simulation finished.")


def cli_menu():
    while True:
        print("\n--- Memory Allocation Simulator ---")
        print("1. Run simulation (First Fit)")
        print("2. Run simulation (Best Fit)")
        print("3. Show memory status")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            reset_memory()
            run_simulation("first_fit")
        elif choice == "2":
            reset_memory()
            run_simulation("best_fit")
        elif choice == "3":
            print_memory()
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice, try again.")


def reset_memory():
    for block in memory:
        block['status'] = 'free'
        block['job'] = None
        block['internal_fragmentation'] = 0
    while not waiting_jobs.empty():
        waiting_jobs.get()


# --------------------------
# Run CLI
# --------------------------
if __name__ == "__main__":
    cli_menu()

'''
# First-fit Algorithm
1. check the memory status to see if there is any available memory block 
that can fit the job size.
2. 


# Best-fit Algorithm
// Alternative:
1. Sort the memory blocks in ascending order based on their sizes. (smallest to largest)
2. so if the first block is too small, the rest will be too.
3. apply merge sort or quick sort


1. Traverse memory blocks
2. Find smallest block that fits the job
3. Allocate job to that block

We also have to mark when a memory block is occupied or free.
2. when the time is up for a job it leaves memory and the space is marked free.
'''


"""
GUI using Tkinter
-> Mimic the layout of memory as square blocks
-> Each block should display its size and status (free/occupied)
-> if free, grey
-> if occupied, red
"""
