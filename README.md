TCPAsynchClient
===============

On service start this block opens a client TCP streaming socket to the selected host address and port. Input signals will be sent to the remote host, while messaged received will be notified from the block.

Properties
----------
- **host**: Host address to connect to
- **message**: Message to send to the connected server
- **port**: Host port to connect to
- **retry_options**: Retry configuration for connection to the server

Inputs
------
- **default**: Upon receipt of any input signal the evaluation of `message` will be sent to `host:port`.

Outputs
-------
- **default**: This block will output a signal for every message received from the remote host with fields `host` and `data`, where `data` can be 8192 bytes.

Commands
--------

Dependencies
------------
None

TCPClient
=========

This block opens a client TCP streaming socket on the selected ip address and port.

Properties
----------
- **expect_response**: Whether to expect a response from the server
- **host**: Host address to connect to
- **message**: Message to send to the connected server
- **port**: Host port to connect to

Inputs
------

Upon receipt of any input signal this block will open a socket connection, send the message, and collect any response.

Outputs
-------

This block will output a 'response' signal containing the response from the socket up to 8192 bytes.

Commands
--------

Dependencies
------------
None

TCPStreamer
===========

This block binds a streaming TCP Server socket on the selected IP address and port. Spawns thread to listen for new remote connections with a backlog queue of 1. Does not send responses to remote clients.

Properties
----------
- **host**: Host address to start a server on
- **port**: Host port to start a server on

Inputs
------

Outputs
-------

Notifies one signal for each received packet (up to 1024 bytes).
-   `data`: Bytefield of packet received
-   `addr`: Tuple of remote client's address and port

Commands
--------
- **current_connections**: 

Dependencies
------------
None
