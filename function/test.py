import websocket
import json

try:
    import thread
except ImportError:
    import _thread as thread
import time


def on_message(ws, message):
    get_message = json.loads(message.decode('utf-8'))
    print(get_message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("close")


def on_open(ws):
    def run(*args):
        sendData = '[{"ticket":"test"},{"type":"ticker","codes":["KRW-CPT","KRW-ADA"]}]'
        ws.send(sendData)
        time.sleep(10)

        ws.close()

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    ws = websocket.WebSocketApp("wss://api.upbit.com/websocket/v1",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
