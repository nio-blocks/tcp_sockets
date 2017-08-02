TCPClient
=========

This block opens a client TCP streaming socket on the selected ip address and port.

Properties
----------
-   **host**: IP address to connect to.
-   **port**: Port to connect on.
-   **message**: Message to send to the socket once connected.

Dependencies
------------
None

Commands
--------
None

Input
-----
Upon receipt of any input signal this block will open a socket connection, send the message, and collect any response.

Output
------
This block will output a 'response' signal containing the response from the socket up to 8192 bytes.

TCPAsynchClient
=========

On service start this block opens a client TCP streaming socket to the selected host address and port. Input signals will be sent to the remote host, while messaged received will be notified from the block.

Properties
----------
-   **host**: Server to connect to.
-   **port**: Port to connect on.
-   **message**: Message to send.

Dependencies
------------
None

Commands
--------
None

Input
-----
Upon receipt of any input signal the evaluation of `message` will be sent to `host:port`.

Output
------
This block will output a signal for every message received from the remote host with fields `host` and `data`, where `data` can be 8192 bytes.

TCPStreamer
===========

This block binds a streaming TCP Server socket on the selected IP address and port. Spawns thread to listen for new remote connections with a backlog queue of 1. Does not send responses to remote clients.

Properties
----------
-   **host**: IP address to bind server
-   **port**: Port to bind server

Dependencies
------------
None

Commands
--------
None

Input
-----
None

Output
------
Notifies one signal for each received packet (up to 1024 bytes).
-   `data`: Bytefield of packet received
-   `addr`: Tuple of remote client's address and port
