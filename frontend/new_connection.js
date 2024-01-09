export function new_connection(param)
{
    const CONNECTION_TIMEOUT = 5000;

    const timeout = setTimeout(() => {
        param.socket.close();
        console.error('WebSocket ' + param.name + ' connection could not be established within the timeout.');
    }, CONNECTION_TIMEOUT);

    param.socket = new WebSocket(param.link);
    /*
        chatSocket.onmessage = function(e) {
            const data = JSON.parse(e.data);
            document.querySelector('#chat-log').value += (data.message + '\n');
        };

        chatSocket.onclose = function(e) {
            console.error('Chat socket closed unexpectedly');
        };

        document.querySelector('#chat-message-input').focus();
        document.querySelector('#chat-message-input').onkeyup = function(e) {
            if (e.key === 'Enter') {  // enter, return
                document.querySelector('#chat-message-submit').click();
            }
        };
     * */
    param.socket.addEventListener('open', (event) => {
        //socket.send(JSON.stringify({ message: 'Hello, server!' }));
        const data = JSON.parse(event.data);
        if ("open" in param.callback)
            param.callback.open(data);
    });
    param.socket.addEventListener('message', (event) => {
        const data = JSON.parse(event.data);
        if ("message" in param.callback)
            param.callback.message(data);
    });
    param.socket.addEventListener('error', (event) => {
        clearTimeout(timeout); // Clear the timeout if there's an error
        this.main.set_status = 'WebSocket ' + param.name + ' error:';
        if ("error" in param.callback)
            param.callback.error();
    });
    param.socket.addEventListener('close', (event) => {
        clearTimeout(timeout); // Clear the timeout if the connection is closed
        this.main.set_status = 'WebSocket ' + param.name + ' connection closed:';
        if ("close" in param.callback)
            param.callback.close();
    });
}
