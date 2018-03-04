#after running this no join error occured anymore Oo?
#src: https://stackoverflow.com/questions/19138219/use-of-threading-thread-join

import time
from threading import *
import queue

que=queue.Queue()

def printer():
    for i in range(1,4):
        time.sleep(1.0)
        print (i)
        que.put(i)


thread = Thread(target=printer)
thread.start()
thread.join()

print("size "+str(que.qsize()) )

n=0
for c in range(que.qsize() ):
    n+=que.get()
    que.task_done()
print(n)

que.join() #expect task_done
print('joined')
