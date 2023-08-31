# 导入所需的库
import tkinter as tk
import asyncio
import websockets
import threading

# 全局变量用于跟踪服务器状态
server_running = False

def get_clash_data():
    # 这里是您的代码来获取从Clash检测出来的流量数据
    return "some_data"

# WebSocket客户端连接函数
async def connect_to_server():
    uri = "ws://localhost:9999"
    #uri = "ws://2pwiyzakfjnmvikqu7la.wgetapi.com:4046"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, Server")

# 定义处理客户端连接的函数
async def handle_client(websocket, path):
    message = await websocket.recv()
    print(f"Received message: {message}")

    if message == "12345678":
        print("Password verified.")
        await websocket.send("VPN Traffic Received")

        while True:
            clash_data = get_clash_data()
            await websocket.send(clash_data)
            await asyncio.sleep(1)

# 启动WebSocket服务器
async def start_websocket_server():
    server = await websockets.serve(handle_client, "localhost", 9999)
    await server.wait_closed()

# 网络服务器模块
def server_and_encryption():
    global server_running

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.run_until_complete(start_websocket_server())

# 网络连接操作模块：启动网络连接
def start_connection():
    global server_running
    server_running = True

    server_thread = threading.Thread(target=server_and_encryption)
    server_thread.start()

    websocket_thread = threading.Thread(target=lambda: asyncio.run(connect_to_server()))
    websocket_thread.start()

# GUI初始化和设置模块
root = tk.Tk()
root.title("ADS VPN系统")
root.state('zoomed')
root.configure(bg='black')

login_button = tk.Button(root, text="Login", command=start_connection)
login_button.pack(side=tk.LEFT, padx=20, pady=20)

connection_button = tk.Button(root, text="连接启动", command=start_connection)
connection_button.pack(side=tk.LEFT, padx=20, pady=20)

root.mainloop()
