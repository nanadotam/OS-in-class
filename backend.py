import simpy
import time
from queue import Queue
from colorama import init, Fore

# initialize colorama
init(autoreset=True)

'''
This program is to simulate inserting jobs into memory blocks in a fixed partition interface.
'''

# --------------------------
# Memory Simulator Class
# --------------------------
class MemorySimulator:
    def __init__(self, jobs, memory):
        self.original_jobs = jobs
        self.original_memory = memory
        self.reset_memory()
        self.env = None
        self.current_time = 0
        self.completed_jobs = []
        self.metrics = MemorySimulatorMetrics()

    # Allocation strategies
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

    # Core memory operations
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

        job['status'] = 'running'
        job['allocated_block'] = block['block']
        self.metrics.job_started()

    def deallocate_memory(self, block):
        # free space in memory 
        finished_job = block['job']
        block['status'] = 'free'
        block['job'] = None
        block['internal_fragmentation'] = 0
        print(Fore.CYAN + f"Job {finished_job['stream']} finished. Block {block['block']} is now free.")
        finished_job['status'] = 'completed'
        self.completed_jobs.append(finished_job)

        # update metrics
        wait_time = finished_job.get('wait_time', 0)
        self.metrics.job_completed(wait_time)

        self.free_waiting_queue()

    # Waiting queue handling
    def waiting_queue(self, job):
        """
        Jobs that cant go in memory go here
        """
        job['queue_entry_time'] = self.env.now  # record queue entry time
        print(Fore.YELLOW + f"Job {job['stream']} of size {job['size']} added to waiting queue at t={self.env.now}.")
        job['status'] = 'queued'
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

    # Simulation processes
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

    def run_simulation(self, strategy):
        self.env = simpy.Environment()
        for job in self.jobs:
            self.env.process(self.job_process(self.env, job, strategy))
        self.env.run()
        print(Fore.CYAN + "Simulation finished.")

    # Step-based simulation for frontend
    def simulate_step(self, strategy="first_fit"):
        if self.env is None:
            self.env = simpy.Environment()
            for job in self.jobs:
                self.env.process(self.job_process(self.env, job, strategy))
        if not self.env.peek() == simpy.core.Infinity:
            self.env.step()
            self.current_time = self.env.now

    # Helpers
    def print_memory(self):
        print("\n=== Memory Status ===")
        for block in self.memory:
            color = Fore.GREEN if block['status'] == 'free' else Fore.RED
            print(color + f"Block {block['block']}: {block['status']} | size={block['size']} | job={block['job']} | waste={block['internal_fragmentation']}")
        print("=====================\n")

    def reset_memory(self):
        self.memory = [dict(block) for block in self.original_memory]
        self.jobs = [dict(job) for job in self.original_jobs]
        for job in self.jobs:
            job['status'] = 'waiting'
            job['wait_time'] = 0
            job['allocated_block'] = None
        self.waiting_jobs = Queue()
        self.completed_jobs = []
        self.metrics = MemorySimulatorMetrics()
        self.env = None
        self.current_time = 0

    # Frontend-friendly getters
    def get_memory_state(self):
        return self.memory

    def get_jobs_state(self):
        return self.jobs

    def get_completed_jobs(self):
        return self.completed_jobs

    def get_waiting_jobs(self):
        return list(self.waiting_jobs.queue)

    def get_metrics(self):
        return {
            "throughput": self.metrics.get_throughput(),
            "avg_wait_time": self.metrics.get_average_waiting_time(),
            "waiting_queue_size": self.metrics.get_waiting_queue_size(),
            "completed_jobs": self.metrics.completed_jobs,
            "total_jobs": self.metrics.total_jobs
        }

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
