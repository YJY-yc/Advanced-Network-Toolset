import http.server
import socketserver
import os
import threading
import wx

# 全局变量
httpd = None
server_thread = None

def start_file_server(port, file_path, directory=None, log_callback=None):
    """
    启动一个简单的HTTP服务器来提供文件服务
    :param port: 监听的端口号
    :param file_path: 要提供的文件路径
    :param directory: 文件所在的目录（可选）
    :param log_callback: 日志回调函数
    """
    global httpd
    
    if directory:
        os.chdir(directory)
    
    class FileHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                # 确保文件路径以/开头
                self.path = '/' + os.path.basename(file_path)
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        def send_head(self):
            # 重写send_head方法，处理非ASCII字符
            path = self.translate_path(self.path)
            try:
                return super().send_head()
            except UnicodeEncodeError:
                # 如果遇到编码错误，将路径转换为ASCII
                path = path.encode('ascii', 'ignore').decode('ascii')
                self.path = path
                return super().send_head()
        
        def translate_path(self, path):
           
            return file_path
        
        def log_message(self, format, *args):
            # 重写log_message方法，将日志信息传递给log_callback
            if log_callback:
                message = "%s - - [%s] %s\n" % (self.address_string(),
                                            self.log_date_time_string(),
                                            format % args)
                log_callback(message)
    httpd = socketserver.TCPServer(("0.0.0.0", port), FileHandler)
    if log_callback:
        import socket
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        log_callback(f"正在端口 {port} 上提供文件服务...\n")
        log_callback(f"本地访问地址: http://localhost:{port}\n")
        log_callback(f"局域网访问地址: http://{ip_address}:{port}\n")
    httpd.serve_forever()

def stop_file_server(log_callback=None):
    """停止文件服务器"""
    global httpd
    if httpd:
        httpd.shutdown()
        httpd.server_close()
        httpd = None
        if log_callback:
            log_callback("服务器已停止\n")

def create_gui():
    """创建图形化界面"""
    app = wx.App()
    frame = wx.Frame(None, title="文件转发", size=(400, 300))
    panel = wx.Panel(frame)
    
    # 控件
    port_label = wx.StaticText(panel, label="端口号:", pos=(10, 20))
    port_text = wx.TextCtrl(panel, pos=(80, 20), size=(100, -1))
    port_text.SetValue("8080")
    
    file_label = wx.StaticText(panel, label="文件路径:", pos=(10, 60))
    file_text = wx.TextCtrl(panel, pos=(80, 60), size=(200, -1))
    
    browse_button = wx.Button(panel, label="浏览...", pos=(290, 60), size=(80, -1))
    
    log_text = wx.TextCtrl(panel, pos=(10, 100), size=(360, 120), 
                          style=wx.TE_MULTILINE|wx.TE_READONLY)
    
    start_button = wx.Button(panel, label="启动", pos=(10, 230), size=(80, -1))
    stop_button = wx.Button(panel, label="停止", pos=(100, 230), size=(80, -1))
    stop_button.Disable()
    
    # 事件处理
    def on_browse(event):
        dlg = wx.FileDialog(frame, "选择要共享的文件", wildcard="All files (*.*)|*.*")
        if dlg.ShowModal() == wx.ID_OK:
            file_text.SetValue(dlg.GetPath())
        dlg.Destroy()
    
    def on_start(event):
        global server_thread
        port = int(port_text.GetValue())
        file_path = file_text.GetValue()
        print(file_path)
        if not os.path.exists(file_path):
            wx.MessageBox("文件不存在！", "错误", wx.OK | wx.ICON_ERROR)
            return
        
        start_button.Disable()
        stop_button.Enable()
        
        server_thread = threading.Thread(
            target=start_file_server,
            args=(port, file_path, os.path.dirname(file_path), lambda msg: wx.CallAfter(log_text.AppendText, msg)),
            daemon=True
        )
        server_thread.start()
    
    def on_stop(event):
        stop_file_server(lambda msg: wx.CallAfter(log_text.AppendText, msg))
        start_button.Enable()
        stop_button.Disable()
    
    # 绑定事件
    browse_button.Bind(wx.EVT_BUTTON, on_browse)
    start_button.Bind(wx.EVT_BUTTON, on_start)
    stop_button.Bind(wx.EVT_BUTTON, on_stop)
    
    frame.Show()
    app.MainLoop()

if __name__ == "__main__":
    create_gui()
