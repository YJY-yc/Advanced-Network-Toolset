import wx
import socket
import threading
import subprocess
from winotify import Notification

toast = Notification(
    app_id="内网聊天",
    title="消息内容",
    msg="消息内容",
    duration="short"  # 或 "long"
)

def create_chat_app():
    app = wx.App()
    frame = wx.Frame(None, title="内网聊天程序", size=(400, 500))
    
    def on_window_message(hwnd, msg, wParam, lParam):
        try:
            # 默认处理所有消息
            return wx.DefaultFrameProc(hwnd, msg, wParam, lParam)
        except Exception as e:
            print(f"消息处理错误: {str(e)}")
            return 0  
    # 初始化UI
    def on_connect_wrapper(event):
        nonlocal sock, server_socket
        sock, server_socket = on_connect(event, controls, sock, server_socket)
        if sock:
            controls['sock'] = sock
    panel, controls = init_ui(frame)
    sock = None
     # 创建新的Notification实例
    controls['toast'] = Notification(
        app_id="内网聊天程序",
        title="新消息",
        duration="short"
    )
    server_socket = None
    def on_connect_wrapper(event):
        nonlocal sock, server_socket
        sock, server_socket = on_connect(event, controls, sock, server_socket)
    # 绑定事件
    frame.Bind(wx.EVT_WINDOW_CREATE, lambda event: frame.SetWindowStyle(wx.DEFAULT_FRAME_STYLE))
    frame.Bind(wx.EVT_CLOSE, lambda event: on_close(event, sock, server_socket))
    controls['toast'] = toast
    controls['start_btn'].Bind(wx.EVT_BUTTON, lambda event: on_start_server(event, controls))
    controls['connect_btn'].Bind(wx.EVT_BUTTON, on_connect_wrapper)
    controls['send_btn'].Bind(wx.EVT_BUTTON, lambda event: on_send(event, controls, sock, toast))
    controls['msg_ctrl'].Bind(wx.EVT_TEXT_ENTER, lambda event: on_send(event, controls, sock, toast))
    controls['port_ctrl'].Bind(wx.EVT_TEXT, lambda event: start_server(event, controls, frame))
    
    frame.Show()
    app.MainLoop()


def start_server(event, controls, frame):
    port = controls['port_ctrl'].GetValue()
    if port and port.isdigit():
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind(('0.0.0.0', int(port)))
            server_socket.listen(1)
            
            def accept_connection():
                while True:
                    sock, addr = server_socket.accept()
                    wx.CallAfter(lambda: on_client_connected(sock, controls, frame))
                    return sock, server_socket
                    
            threading.Thread(target=accept_connection, daemon=True).start()
            
            return server_socket
        except Exception as e:
            wx.MessageBox(f"启动服务器失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    return None
def on_client_connected(sock, controls, frame):
    controls['ip_ctrl'].SetValue("已连接")
    controls['connect_btn'].Disable()
    threading.Thread(target=receive_messages, args=(sock, controls), daemon=True).start()
    
    # 获取对方IP地址
    client_ip = sock.getpeername()[0]
    
    
    try:
        # 使用新socket连接对方，使用不同的端口号
        reverse_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reverse_port = int(controls['port_ctrl'].GetValue()) + 1  # 使用原端口号+1
        reverse_sock.connect((client_ip, reverse_port))
        threading.Thread(target=receive_messages, args=(reverse_sock, controls), daemon=True).start()
        
        # 更新controls中的sock
        controls['sock'] = reverse_sock  # 确保更新了controls中的sock
        wx.MessageBox(f"已成功连接对方 {client_ip}:{reverse_port}", "提示", wx.OK | wx.ICON_INFORMATION)
    except Exception as e:
        wx.MessageBox(f"自动连接对方失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    
    # 同时保存原始连接
    controls['original_sock'] = sock
    return sock
def init_ui(frame):
    panel = wx.Panel(frame)
    vbox = wx.BoxSizer(wx.VERTICAL)
    
    # 连接设置
    hbox1 = wx.BoxSizer(wx.HORIZONTAL)
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)
    show_btn = wx.Button(panel, label="显示消息")
    hbox3.Add(show_btn, 0, wx.ALL, 5)
    show_btn = wx.Button(panel, label="显示消息")
    export_btn = wx.Button(panel, label="导出记录")
    hbox3.Add(show_btn, 0, wx.ALL, 5)
    hbox3.Add(export_btn, 0, wx.ALL, 5)
    ip_ctrl = wx.TextCtrl(panel, value="127.0.0.1")
    port_ctrl = wx.TextCtrl(panel, value="5000")
    connect_btn = wx.Button(panel, label="连接")
    start_btn = wx.Button(panel, label="启动服务")  # 新增启动服务按钮
    hbox1.Add(ip_ctrl, 1, wx.EXPAND|wx.ALL, 5)
    hbox1.Add(port_ctrl, 0, wx.EXPAND|wx.ALL, 5)
    hbox1.Add(connect_btn, 0, wx.ALL, 5)
    hbox1.Add(start_btn, 0, wx.ALL, 5)
    
    # 聊天记录
    chat_list = wx.ListBox(panel, style=wx.LB_SINGLE)
    msg_display = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
    
    vbox.Add(hbox3, 0, wx.EXPAND|wx.ALL, 5)
    vbox.Add(msg_display, 1, wx.EXPAND|wx.ALL, 5)
    
    # 绑定显示按钮事件
    def on_show_message(event):
        selection = chat_list.GetSelection()
        if selection != wx.NOT_FOUND:
            msg = chat_list.GetString(selection)
            msg_display.SetValue(msg)
        else:
            wx.MessageBox("请先选择一条消息", "提示", wx.OK | wx.ICON_INFORMATION)
    
    show_btn.Bind(wx.EVT_BUTTON, on_show_message)
    # 消息输入
    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    msg_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
    send_btn = wx.Button(panel, label="发送")
    hbox2.Add(msg_ctrl, 1, wx.EXPAND|wx.ALL, 5)
    hbox2.Add(send_btn, 0, wx.ALL, 5)
    
    # 消息类型选择
    msg_type = wx.RadioBox(panel, label="消息类型", choices=["普通消息", "加急消息", "命令行"])
    
    vbox.Add(hbox1, 0, wx.EXPAND|wx.ALL, 5)
    vbox.Add(chat_list, 1, wx.EXPAND|wx.ALL, 5)
    vbox.Add(msg_type, 0, wx.EXPAND|wx.ALL, 5)
    vbox.Add(hbox2, 0, wx.EXPAND|wx.ALL, 5)
    
    panel.SetSizer(vbox)
    
    controls = {
        'ip_ctrl': ip_ctrl,
        'port_ctrl': port_ctrl,
        'connect_btn': connect_btn,
        'start_btn': start_btn,  # 添加启动按钮到controls
        'chat_list': chat_list,
        'msg_ctrl': msg_ctrl,
        'send_btn': send_btn,
        'msg_type': msg_type,
        'msg_display': msg_display
    }
    def on_export_chat(event):
        with wx.FileDialog(frame, "导出聊天记录", wildcard="Text files (*.txt)|*.txt",
                          style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # 用户取消

            # 保存文件路径
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'w', encoding='utf-8') as f:
                    for i in range(chat_list.GetCount()):
                        f.write(chat_list.GetString(i) + '\n')
                wx.MessageBox(f"聊天记录已成功导出到 {pathname}", "成功", wx.OK | wx.ICON_INFORMATION)
            except IOError:
                wx.MessageBox(f"无法保存文件 {pathname}", "错误", wx.OK | wx.ICON_ERROR)

    export_btn.Bind(wx.EVT_BUTTON, on_export_chat)
    return panel, controls



def on_start_server(event, controls):
    port = controls['port_ctrl'].GetValue()
    if port and port.isdigit():
        try:
            # 获取本机IP地址
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            
            # 更新IP显示
            controls['ip_ctrl'].SetValue(ip)
            controls['ip_ctrl'].Disable()
            controls['connect_btn'].Disable()
            controls['start_btn'].Disable()
            
            # 启动服务器
            server_socket = start_server(event, controls, None)
            if server_socket:
                wx.MessageBox(f"已启动，IP: {ip}，等待连接...", "提示", wx.OK | wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"启动失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
def on_connect(event, controls, sock, server_socket):
    ip = controls['ip_ctrl'].GetValue()
    port = int(controls['port_ctrl'].GetValue())
    
    try:
        # 如果是自连接，先启动服务器
        if ip == "127.0.0.1" or ip == "localhost":
            if not server_socket:
                server_socket = start_server(event, controls, None)
                if not server_socket:
                    return None
                    
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            threading.Thread(target=receive_messages, args=(sock, controls), daemon=True).start()
            
            # 启动反向连接监听
            reverse_port = port + 1
            reverse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            reverse_socket.bind(('0.0.0.0', reverse_port))
            reverse_socket.listen(1)
            threading.Thread(target=accept_reverse_connection, args=(reverse_socket, controls), daemon=True).start()
            
            wx.MessageBox("自连接成功", "提示", wx.OK | wx.ICON_INFORMATION)
            controls['sock'] = sock
            controls['start_btn'].Disable()  
            controls['connect_btn'].Disable()  
            
            # 锁定启动服务按钮
            return sock, server_socket
                
        # 正常连接其他服务器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        threading.Thread(target=receive_messages, args=(sock, controls), daemon=True).start()
        
        # 启动反向连接监听
        reverse_port = port + 1
        reverse_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        reverse_socket.bind(('0.0.0.0', reverse_port))
        reverse_socket.listen(1)
        threading.Thread(target=accept_reverse_connection, args=(reverse_socket, controls), daemon=True).start()
        
        wx.MessageBox("连接成功", "提示", wx.OK | wx.ICON_INFORMATION)
        controls['sock'] = sock
        controls['start_btn'].Disable()  # 锁定启动服务按钮
    except Exception as e:
        wx.MessageBox(f"连接失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
    return sock, server_socket

def accept_reverse_connection(reverse_socket, controls):
    while True:
        sock, addr = reverse_socket.accept()
        controls['sock'] = sock
        threading.Thread(target=receive_messages, args=(sock, controls), daemon=True).start()

def on_send(event, controls, sock, toast):
    # 优先使用controls中的sock
    active_sock = controls.get('sock', sock)
    if not active_sock:
        # 尝试使用原始连接
        active_sock = controls.get('original_sock')
        if not active_sock:
            wx.MessageBox("请先连接", "错误", wx.OK | wx.ICON_ERROR)
            return
        
    msg = controls['msg_ctrl'].GetValue()
    if not msg:
        return
        
    msg_type = controls['msg_type'].GetSelection()
    prefix = "-m"  # 默认普通消息
    if msg_type == 1:
        prefix = "-q"
    elif msg_type == 2:
        prefix = "-c"
        
    full_msg = f"{prefix} {msg}"
    try:
        active_sock.send(full_msg.encode())  # 使用active_sock发送消息
        controls['chat_list'].Append(f"> {msg}")
        controls['msg_ctrl'].Clear()
    except Exception as e:
        wx.MessageBox(f"发送失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
def receive_messages(sock, controls):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                print("连接已关闭")
                break
                
            prefix, msg = data[:2], data[3:]
            
            if prefix == "-m":
                controls['chat_list'].Append(f"对方: {msg}")
            elif prefix == "-q":
                controls['chat_list'].Append(f"对方（加急）: {msg}")
                
                if 'toast' in controls:
                    try:
                        
                        controls['toast'].msg = msg
                        controls['toast'].title = msg
                        wx.CallAfter(controls['toast'].show)
                    except Exception as e:
                        print(f"显示通知失败: {str(e)}")
            elif prefix == "-c":
                confirm = wx.MessageBox(f"对方请求执行命令: {msg}\n是否允许？", 
                                      "命令确认", 
                                      wx.YES_NO | wx.ICON_QUESTION)
                if confirm == wx.YES:
                    try:
                        output = subprocess.check_output(msg, shell=True)
                        sock.send(f"-m {output.decode()}".encode())
                    except Exception as e:
                        sock.send(f"-m 命令执行失败: {str(e)}".encode())
                        
        except ConnectionResetError:
            print("对方强制关闭了连接")
            break
        except ConnectionAbortedError:
            print("连接被中止")
            break
        except Exception as e:
            print(f"接收消息时发生错误: {str(e)}")
            # 继续接收消息而不是直接断开连接
            continue

def on_close(event, sock, server_socket):
    try:
        if sock:
            sock.shutdown(socket.SHUT_RDWR)  # 优雅地关闭socket
            sock.close()
        if server_socket:
            server_socket.close()
    except Exception as e:
        print(f"关闭socket时发生错误: {str(e)}")
    event.Skip()

if __name__ == "__main__":
    create_chat_app()
