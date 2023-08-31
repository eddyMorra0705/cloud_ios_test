# 導入所需模塊
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import psutil
import time

# 全局變量模塊
interface_name = None  # 當前選擇的網絡接口名稱
data_gen_t = None  # 數據生成器
ani = None  # 動畫對象

# 網絡接口選擇模塊
def get_interface():
    # 獲取所有網絡接口的名稱
    interface_names = list(psutil.net_io_counters(pernic=True).keys())
    # 打印偵測到的所有網絡接口
    print("Detected Network Interfaces:", interface_names)  # 新增這一行
    # 創建一個新的窗口來顯示接口選項
    interface_choice = tk.Toplevel(root)
    interface_choice.title("選擇網絡接口")
    tk.Label(interface_choice, text="請選擇要監控的網絡接口：").pack()
    for name in interface_names:
        tk.Button(interface_choice, text=name, command=lambda n=name: choose_interface(n)).pack()

# 更新當前選擇的網絡接口模塊
def choose_interface(name):
    global interface_name, ani
    interface_name = name
    if ani:
        ani.event_source.stop()
    ax.set_title(f'{interface_name} - Signal Detection', color='white')
    start_animation()

# 數據生成模塊
def data_gen():
    global interface_name
    t = 0
    old_value = psutil.net_io_counters(pernic=True)[interface_name].bytes_recv
    while True:
        new_value = psutil.net_io_counters(pernic=True)[interface_name].bytes_recv
        t += 1
        yield t, (new_value - old_value) / (1024 ** 3)  # 單位轉換為千兆字節（gigabytes）
        old_value = new_value
        time.sleep(1)

# 數據更新模塊
def update(frame):
    time, value = next(data_gen_t)
    xdata = list(line.get_xdata()) + [time]
    ydata = list(line.get_ydata()) + [value]
    if len(xdata) > 10:
        xdata = xdata[-10:]
        ydata = ydata[-10:]
    line.set_xdata(xdata)
    line.set_ydata(ydata)
    ax.relim()
    ax.autoscale_view()
    return line,

# 動畫啟動模塊
def start_animation():
    global ani, data_gen_t
    data_gen_t = data_gen()
    ani = animation.FuncAnimation(fig, update, blit=False, interval=1000, cache_frame_data=False)
    ani._start()

# GUI界面結構模塊
root = tk.Tk()
root.title("WiFi Signal Detection")
root.geometry("800x600")

# 圖表模塊
fig = Figure(figsize=(5, 3), facecolor='#1e1e1e')
ax = fig.add_subplot(1, 1, 1, facecolor='#1e1e1e')
ax.tick_params(color='white', labelcolor='white')
for spine in ax.spines.values():
    spine.set_edgecolor('white')
line, = ax.plot([], [], lw=2, color='#00ff00')
ax.set_xlabel('Time (s)', color='white')
ax.set_ylabel('WiFi Traffic (GB)', color='white')  # 更新Y軸單位為千兆字節
ax.set_title('Signal Detection', color='white')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# 接口選擇按鈕模塊
choose_interface_btn = tk.Button(root, text="Choose Network Interface", command=get_interface)
choose_interface_btn.pack()

# 主事件循環模塊
root.mainloop()
