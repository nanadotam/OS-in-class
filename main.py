import simpy
import tkinter as tk
# applying a queue for waiting jobs
from queue import Queue

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




# Define functions

def first_fit(jobs, memory):
    # 1. check the memory status to see if there is any available memory block that can fit the job size.
    for job in jobs:
        for block in memory:
            if block['status'] == 'free' and block['size'] >= job['size']:
                allocate_memory(job, block)
                break
        else:
            print(f"Job {job['stream']} of size {job['size']} cannot be allocated.")
    pass

def best_fit(jobs, memory):
    #  sort the memory block in ascending order based on their sizes.
    memory = sorted(memory, key=lambda x: x['size'])
    # check the size of the incoming job against the memory blocks.
    for job in jobs:
        for block in memory:
            if block['status'] == 'free' and block['size'] >= job['size']:
                allocate_memory(job, block)
                break
        else:
            print(f"Job {job['stream']} of size {job['size']} cannot be allocated.")
   
   
   
   
    pass

def allocate_memory(job, block):
    # assign the job
    block['status'] = 'occupied'
    # we need to show somewhere that a job is in a memory block.
    # after we put it in the memory, we need to know how much of the memory is being used and how much is wasted.
    # 2. calculate internal fragmentation
    size_wasted = block['size'] - job['size']

    block['internal_fragmentation'] = size_wasted

    # when a job leaves the memory block the internal fragmentation is set back to 0
    # block['internal_fragmentation'] = 0

    pass


# waiting queue function
# FIFO
def waiting_queue(jobs, memory):
    # so if a job wants to enter memory
    # either the memory blocks are occupied
    # OR its too big for the memory blocks
    # we assign it into this waiting queue


    # we need a case for when a job leaves memory or when a space is free

    # we need a way to keep
    pass





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
