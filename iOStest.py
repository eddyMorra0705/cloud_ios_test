# 导入Kivy库的相关模块
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.clock import Clock
import asyncio
import websockets
import threading  # 新增: 导入 threading 模块
from websocket import create_connection  # 新增: 导入 create_connection 函数

# 在這裡初始化一個 asyncio 事件循環
loop = asyncio.get_event_loop()

# ------------------ WebSocket连接模块 ------------------

# 新增一个全局变量用于 WebSocket 连接
websocket = None

# 新增一个全局变量用于 WebSocket 线程
websocket_thread = None
# 新增一个全局变量用于跟踪连接状态
is_connected = False  # 在这里定义全局变量

# 新增一个全局变量用于 WebSocket 任务
websocket_task = None  # 在这里定义全局变量

# 在這裡添加一個全局變量來跟踪是否應該停止接收數據
should_stop = False  # 在這裡定義全局變量

# 新增函数用于连接到 main2.py 的WebSocket服务器
def receive_vpn_traffic(label):
    global should_stop, websocket
    websocket = create_connection("ws://localhost:9999")
    websocket.send("12345678")
    received_traffic = 0.0  # 初始化流量计数器
    while not should_stop:
        received_message = websocket.recv()
        print(f"Received message: {received_message}")
        if received_message == "some_data":
            received_traffic += 0.1  # 假设每次接收到 "some_data" 时，都表示检测到了0.1MB的流量
            # 更新标签文本以显示接收到的流量数据
            label.text = f'Received WiFi Traffic: {received_traffic} MB'
        else:
            try:
                # 尝试将接收到的消息转换为浮点数
                additional_traffic = float(received_message)
                received_traffic += additional_traffic
                # 更新标签文本以显示接收到的流量数据
                label.text = f'Received WiFi Traffic: {received_traffic} MB'
            except ValueError:
                print(f"Could not convert message to float: {received_message}")
#
# ------------------ 自定义按钮模块 ------------------
# 自定义一个圆形按钮
class CircleButton(Button):
    def __init__(self, **kwargs):
        super(CircleButton, self).__init__(**kwargs)
        # 设置按钮的背景颜色和文字颜色
        self.background_color = (0, 0, 0, 0)
        self.color = (1, 1, 1, 1)
        # 绑定位置和大小变化事件到重绘函数
        self.bind(pos=self.redraw, size=self.redraw)

    def redraw(self, *args):
        # 清除当前画布
        self.canvas.before.clear()
        # 在画布上绘制红色的圆形
        with self.canvas.before:
            Color(1, 0, 0, 1)
            Ellipse(pos=self.pos, size=self.size)

# ------------------ 主应用模块 ------------------
# 主应用类
class MainApp(App):
    def build(self):
        # 创建一个浮动布局
        layout = FloatLayout(size=(300, 300))
        # 设置布局的背景颜色为黑色
        with layout.canvas.before:
            Color(0, 0, 0, 1)
            self.rect = Rectangle(size=layout.size, pos=layout.pos)

        # 创建一个自定义的红色圆形按钮
        btn = CircleButton(text='Connect',
                           size_hint=(None, None),
                           size=(100, 100),
                           pos_hint={'center_x': .5, 'center_y': .5})

        # 绑定按钮的按下事件到连接服务器的函数
        btn.bind(on_press=self.toggle_connection)

        # 创建一个标签用于显示接收到的WiFi流量
        self.label = Label(text='Received WiFi Traffic: 0 GB',
                           size_hint=(.5, .1),
                           pos_hint={'center_x': .5, 'center_y': .1})

        # 将按钮和标签添加到布局中
        layout.add_widget(btn)
        layout.add_widget(self.label)

        return layout

    # 在 toggle_connection 函数中，当用户点击 "Disconnect" 时，设置 should_stop 为 True
    def toggle_connection(self, instance):
        global is_connected, websocket_task, should_stop, websocket, websocket_thread
        if not is_connected:
            should_stop = False
            instance.text = "Disconnect"
            with instance.canvas.before:
                Color(0, 0, 1, 1)
            instance.redraw()
            websocket_thread = threading.Thread(target=receive_vpn_traffic, args=(self.label,))
            websocket_thread.start()
            is_connected = True
        else:
            should_stop = True
            instance.text = "Connect"
            with instance.canvas.before:
                Color(1, 0, 0, 1)
            instance.redraw()
            if websocket_thread:
                websocket_thread.join()
            if websocket:  # 如果 websocket 存在
                websocket.close()  # 关闭 websocket 连接
            is_connected = False

# ------------------ 程序入口 ------------------
# 程序入口
if __name__ == '__main__':
    MainApp().run()