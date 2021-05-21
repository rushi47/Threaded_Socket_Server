# Threaded TCP Socket Server
- Extended existing python TCP Server to support the functionality of Threads.
- Base python TCP Server runs on Single Thread.
- Setup:
  - Clone the repository
  - Code runs with python3
  - python3 Threaded_TCP_Server.py
  - Threads can be controlled by "no_of_socket_threads" parameter and is defined in main block.
 
- TO DOs:
  - Code starts with threads defined, so even if its not serving any request, as soon as threads are spawned its going to consume the constant
    amount of memory.
  - Solution of the problem is implementing the Thread Executor Pool of python.
  - But the problem with Thread Executor Pool, is it doesn't grows and shrinks Dynamically.
  - Thread Executor Pools problem of Dynamic Shrinking and Scaling can also be solved by implementing 
    side car thread, which kills the spawned ideal threads. 
