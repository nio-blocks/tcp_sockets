TCPclient
===========

This block opens a client TCP streaming socket on the selected ip address and port.

Properties
--------------
-   **IP_addr**: IP address to connect to.
-   **port**: Port to connect on.
-   **message**: Message to send to the socket once connected.
-   **add_newline**: Add a newline charactor to the end of the message to send.

Dependencies
----------------
None

Commands
----------------
None

Input
-------
Upon receipt of any input signal this block will open a socket connection, send the message, and collect any response.

Output
---------
This block will output a 'response' signal containing the response from the socket up to 8192 bytes.



TCPserver
===========

This block binds a streaming TCP Server socket on the selected IP address and port. Spawns thread to listen for new remote connections with a backlog queue of 1.

Properties
--------------
-   **IP_addr**: IP address to connect to.
-   **port**: Port to connect on.
-   **Response**: Message to send to a previously connected client.
-   **Client IP/Port**: The client's address and port for sending response

Dependencies
----------------
None

Commands
----------------
None

Input
-------
Used for sending response messages. Evaluation of `Client IP/Port` must be a tuple in the format of ('address', port). To send no response message, do connect an input signal, otherwise the output signal is to be processed and returned to the block's input. If the remote client has disconnected and exception will be logged.

Output
---------
Outputs a signal upon connection and recepit of data (up to 8192 bytes) from remote client. Each signal contains `addr` field (tuple) to be used for sending response.
