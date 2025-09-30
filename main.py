import simpy
import tkinter as tk
# applying a queue for waiting jobs
from queue import Queue
from colorama import init, Fore, Style
import time  # added for real-time delay

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

# --------------------------
# Memory Simulator Class
# --------------------------
class MemorySimulator:
    def __init__(self, jobs, memory):
        self.jobs = jobs
        self.memory = memory
        self.waiting_jobs = Queue()
        self.env = None

    def first_fit(self, job):
        # 1. check the memory status to see if there is any available memory block that can fit the job size.
        for block in self.memory:
            if block['status'] == 'free' and block['size'] >= job['size']:
                self.allocate_memory(job, block)
                return block
        print(Fore.RED + f"Job {job['stream']} of size {job['size']} cannot be allocated.")
        return None

    def best_fit(self, job):
        #  sort the memory block in ascending order based on their sizes.
        for block in sorted(self.memory, key=lambda x: x['size']):
            if block['status'] == 'free' and block['size'] >= job['size']:
                self.allocate_memory(job, block)
                return block
        print(Fore.RED + f"Job {job['stream']} of size {job['size']} cannot be allocated.")
        return None

    def allocate_memory(self, job, block):
        # assign the job
        block['status'] = 'occupied'
        block['job'] = job
        size_wasted = block['size'] - job['size']
        block['internal_fragmentation'] = size_wasted
        if 'queue_entry_time' in job:  # calculate wait time if job came from queue
            wait_time = self.env.now - job['queue_entry_time']
            job['wait_time'] = wait_time
            print(Fore.GREEN + f"Job {job['stream']} allocated to Block {block['block']} (waste={size_wasted}, waited {wait_time}).")
        else:
            print(Fore.GREEN + f"Job {job['stream']} allocated to Block {block['block']} (waste={size_wasted}).")

    def deallocate_memory(self, block):
        # free space in memory 
        finished_job = block['job']
        block['status'] = 'free'
        block['job'] = None
        block['internal_fragmentation'] = 0
        print(Fore.CYAN + f"Job {finished_job['stream']} finished. Block {block['block']} is now free.")
        self.free_waiting_queue()

    # waiting queue function
    # FIFO
    def waiting_queue(self, job):
        """
        Jobs that cant go in memory go here
        """
        job['queue_entry_time'] = self.env.now  # record queue entry time
        print(Fore.YELLOW + f"Job {job['stream']} of size {job['size']} added to waiting queue at t={self.env.now}.")
        self.waiting_jobs.put(job)

    def free_waiting_queue(self):
        """
        Frees up the waiting queue after a job has been entered
        """
        if self.waiting_jobs.empty():
            return

        for _ in range(self.waiting_jobs.qsize()):
            job = self.waiting_jobs.get()
            for block in self.memory:
                if block['status'] == 'free' and block['size'] >= job['size']:
                    self.allocate_memory(job, block)
                    print(Fore.MAGENTA + f"Job {job['stream']} allocated from waiting queue to block {block['block']} at t={self.env.now}.")
                    break
            else:
                self.waiting_jobs.put(job)
                print(Fore.RED + f"Job {job['stream']} remains in waiting queue.")
                break

    def job_process(self, env, job, strategy="first_fit"):
        if strategy == "first_fit":
            b = self.first_fit(job)
        else:
            b = self.best_fit(job)

        if b is None:
            self.waiting_queue(job)
        else:
            yield env.timeout(job['time'])
            time.sleep(1)  # slow down for visualization
            self.deallocate_memory(b)

    def print_memory(self):
        print("\n=== Memory Status ===")
        for block in self.memory:
            color = Fore.GREEN if block['status'] == 'free' else Fore.RED
            print(color + f"Block {block['block']}: {block['status']} | size={block['size']} | job={block['job']} | waste={block['internal_fragmentation']}")
        print("=====================\n")

    def run_simulation(self, strategy):
        self.env = simpy.Environment()
        for job in self.jobs:
            self.env.process(self.job_process(self.env, job, strategy))
        self.env.run()
        print(Fore.CYAN + "Simulation finished.")

    def reset_memory(self):
        for block in self.memory:
            block['status'] = 'free'
            block['job'] = None
            block['internal_fragmentation'] = 0
        while not self.waiting_jobs.empty():
            self.waiting_jobs.get()


# --------------------------
#calculating metrics
# Throughput: number of jobs completed per unit time
# Waiting Time: total time a job spends in the system (waiting + execution)
# Waiting Queue: number of jobs waiting to be allocated memory in the queue
# --------------------------
class MemorySimulatorMetrics:
    def __init__(self):
        self.total_jobs = 0
        self.completed_jobs = 0
        self.total_waiting_time = 0
        self.waiting_jobs = 0

    def job_started(self):
        self.total_jobs += 1
        self.waiting_jobs += 1

    def job_completed(self, waiting_time):
        self.completed_jobs += 1
        self.total_waiting_time += waiting_time
        self.waiting_jobs -= 1

    def get_throughput(self):
        return self.completed_jobs / self.total_jobs if self.total_jobs > 0 else 0

    def get_average_waiting_time(self):
        return self.total_waiting_time / self.completed_jobs if self.completed_jobs > 0 else 0

    def get_waiting_queue_size(self):
        return self.waiting_jobs


# --------------------------
# CLI Menu
# --------------------------
def cli_menu():
    sim = MemorySimulator(jobs, memory)
    while True:
        print("\n--- Memory Allocation Simulator ---")
        print("1. Run simulation (First Fit)")
        print("2. Run simulation (Best Fit)")
        print("3. Show memory status")
        print("4. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            sim.reset_memory()
            sim.run_simulation("first_fit")
        elif choice == "2":
            sim.reset_memory()
            sim.run_simulation("best_fit")
        elif choice == "3":
            sim.print_memory()
        elif choice == "4":
            print("Exiting program.")
            break
        else:
            print("Invalid choice, try again.")


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
