import threading

barrier = threading.Barrier(2)
thread_local = threading.local()

def f(n):
    set_local_x(n)

def get_local_x():
    try:
        return thread_local.x
    except AttributeError as e:
        return "Local x not yet set"

def set_local_x(n):
    thread_local.x = n

thread1 = threading.Thread(target=f, args=(1,))
thread2 = threading.Thread(target=f, args=(2,))
thread1.start()
thread2.start()
thread_local.
thread1.thre
print(thread1.)