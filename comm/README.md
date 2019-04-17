node and server instances.
changes to be made when integrating with simulator and 2pc.

pseudocode of the flow of control:
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
