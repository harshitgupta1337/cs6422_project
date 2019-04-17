#### Communnication setup 
- node and server instances.
- changes to be made when integrating with simulator and 2pc.

**Library used: ZeroMQ**
</br>
ØMQ is a lightweight and fast messaging implementation. It acts like a concurrency framework. It gives you sockets that carry atomic messages across various transports like in-process, inter-process, TCP, and multicast. You can connect sockets N-to-N with patterns like fan-out,pub-sub, task distribution, and request-reply. It’s fast enough to be the fabric for clustered products. Its asynchronous I/O model gives you scalable multicore applications, built as asynchronous message-processing tasks. It has a score of language APIs and runs on most operating systems. 

**Pseudocode of the flow of control:**
</br>
```
prepare context, frontend and backend sockets
        while true:
            poll on both sockets
            if frontend had input:
                read all frames from frontend
                send to backend
            if backend had input:
                read all frames from backend
                send to frontend
```


