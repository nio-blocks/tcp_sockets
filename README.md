TCPSocket
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
