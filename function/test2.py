import websocket

websocket.connect('wss://api.upbit.com/websocket/v1')
ss = '[{"ticket":"test1243563456"},{"type":"trade","codes":["KRW-BTC", "KRW-ETH"]}]'

websocket.send(ss)
data_rev = websocket.recv()