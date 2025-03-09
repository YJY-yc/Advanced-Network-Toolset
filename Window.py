import wx
import os
import htmls, time
import CommanDownload
from os import makedirs
import MultiThreadedDownloadFunction
import wx.adv
import os
import requests
from bs4 import BeautifulSoup
import analyze
import json
import sys
import threading,TPort
from TPort import *
from ChatPort import *
from winotify import Notification












vision = "3.5.1.3"
url_text_1, filename_text_1 = "", ""

listbook=None
url_text_analyze=None



roaming_path = os.getenv('APPDATA') + ''

target_folder = os.path.join(roaming_path, "NetDownloader")

if not os.path.exists(target_folder):
    os.makedirs(target_folder)
print(target_folder)
if not os.path.exists(target_folder + "\dir.txt"):
    with open(target_folder + "\dir.txt", "w") as f:
        f.write("D:/Downloads/")
f=open(target_folder+"\dir.txt","r")
dirs=f.read()
f.close()
if dirs=="":
    dirs="D:/Downloads/"
    f=open(target_folder+"\dir.txt","w")
    
    f.write(dirs)
    f.close()
print(dirs)

try:
    makedirs(dirs)
except:
    pass
    
try:
    makedirs(dirs+"temp/")
except:
        pass
config = {
    'font_size': 17,
    'list_button_size': 15,
    'font_name': "微软雅黑",
    'size': (300, 30),
    'size_button': (100, 30),
    'window_pos': (100, 20),  
    'window_size': [800, 500]  
}

if not os.path.exists(target_folder):
    os.makedirs(target_folder)

config_path = os.path.join(target_folder, "config.json")
if os.path.exists(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config.update(json.load(f))
    except:
       
        pass
else:
   
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


FontSize = config['font_size']
ListButtonSize = config['list_button_size']
fontname = config['font_name']
Size = tuple(config['size'])
SizeButton = tuple(config['size_button'])
windowPos = tuple(config['window_size'])







##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################








def init_chat_ui(panel):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 连接设置
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        ip_ctrl = wx.TextCtrl(panel, value="127.0.0.1")
        port_ctrl = wx.TextCtrl(panel, value="5000")
        connect_btn = wx.Button(panel, label="连接到...")
        start_btn = wx.Button(panel, label="启动服务")
        hbox1.Add(ip_ctrl, 1, wx.EXPAND|wx.ALL, 5)
        hbox1.Add(port_ctrl, 0, wx.EXPAND|wx.ALL, 5)
        hbox1.Add(connect_btn, 0, wx.ALL, 5)
        hbox1.Add(start_btn, 0, wx.ALL, 5)
        
        # 聊天记录
        chat_list = wx.ListBox(panel, style=wx.LB_SINGLE, size=(400, 200))
        
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
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        show_btn = wx.Button(panel, label="显示消息")
        
        hbox3.Add(show_btn, 0, wx.ALL, 5)
        export_btn = wx.Button(panel, label="导出记录")
       
        hbox3.Add(export_btn, 0, wx.ALL, 5)
        panel.SetSizer(vbox)
        # 添加消息显示文本框
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
        # 保存控件引用
        controls = {
        'ip_ctrl': ip_ctrl,
        'port_ctrl': port_ctrl,
        'connect_btn': connect_btn,
        'start_btn': start_btn,
        'chat_list': chat_list,
        'msg_ctrl': msg_ctrl,
        'send_btn': send_btn,
        'msg_type': msg_type,
        'sock': None,
        'msg_display': msg_display,
        'server_socket': None,
        'toast': Notification(
            app_id="内网聊天程序",
            title="新消息",
            duration="short"
        )  # 使用winotify的Notification
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
    
        # 修改事件绑定
        connect_btn.Bind(wx.EVT_BUTTON, lambda event: on_connect(event, controls, controls['sock'], controls['server_socket']))
        start_btn.Bind(wx.EVT_BUTTON, lambda event: on_start_server(event, controls))
        send_btn.Bind(wx.EVT_BUTTON, lambda event: on_send(event, controls, controls['sock'], controls['toast']))
        msg_ctrl.Bind(wx.EVT_TEXT_ENTER, lambda event: on_send(event, controls, controls['sock'], controls['toast']))







def on_analyze(event):
    global url_text_analyze
    analyze.on_analyze_button(url_text_analyze.GetValue())

def options(event):
    global dirs
    global Pos
    Pos = config.get('window_pos', (100, 20))  
    options_window = wx.Frame(None, title="首选项", size=(400, 500))
    notebook = wx.Notebook(options_window,pos=(0,0))
    window = wx.Panel(notebook)
    file_panel = wx.Panel(notebook)
    storage_panel = wx.Panel(notebook)
    manage_panel = wx.Panel(notebook)
    port_panel = wx.Panel(notebook)

    wx.StaticText(port_panel, label="默认端口:", pos=(10, 0))
    port_ctrl = wx.SpinCtrl(port_panel, value=str(config.get('default_port', 1524)), 
                          pos=(100, 0), min=1024, max=65535)
    
    # 添加自动打开浏览器选项
    auto_open_browser = wx.CheckBox(port_panel, label="启动后自动打开浏览器", 
                                  pos=(10, 80))
    auto_open_browser.SetValue(config.get('auto_open_browser', True))
    wx.StaticText(window, label="选择字体:", pos=(10, 10))
    font_choices = wx.FontEnumerator().GetFacenames() 
    font_choice = wx.Choice(window, pos=(100, 10), size=(150, -1), choices=font_choices)
    font_choice.SetStringSelection(config['font_name'])
    def update_font_preview(event=None):
        selected_font = font_choice.GetStringSelection()
        font_preview.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, 
                                   wx.FONTWEIGHT_NORMAL, faceName=selected_font))
        font_preview.SetLabel("中国智造，惠及全球ABC")
    wx.StaticText(window, label="字体浏览:", pos=(1, 280))
    font_preview = wx.StaticText(window, label="中国智造，惠及全球ABC", pos=(1, 300))
    update_font_preview() 
    font_choice.Bind(wx.EVT_CHOICE, update_font_preview)
  

    wx.StaticText(window, label="字体大小:", pos=(10, 45))
    font_size_ctrl = wx.SpinCtrl(window, value=str(config['font_size']), pos=(100, 45), min=10, max=30)
    
 
    wx.StaticText(window, label="控件宽度:", pos=(10, 80))
    width_ctrl = wx.SpinCtrl(window, value=str(config['size'][0]), pos=(100, 80), min=100, max=500)
    
    wx.StaticText(window, label="控件高度:", pos=(10, 120))
    height_ctrl = wx.SpinCtrl(window, value=str(config['size'][1]), pos=(100, 120), min=20, max=100)
    

    wx.StaticText(window, label="窗口位置 XY:", pos=(10, 160))
    pos_x_ctrl = wx.SpinCtrl(window, value=str(Pos[0]), pos=(100, 160), min=0, max=1920)
    
    
    pos_y_ctrl = wx.SpinCtrl(window, value=str(Pos[1]), pos=(170, 160), min=0, max=1080)

    wx.StaticText(window, label="窗口大小:", pos=(10, 200))
    width_ctrl = wx.SpinCtrl(window, value=str(frame.GetSize().GetWidth()), pos=(100, 200), min=400, max=1920)

    height_ctrl = wx.SpinCtrl(window, value=str(frame.GetSize().GetHeight()), pos=(170, 200), min=300, max=1080)

    def on_save_config(event):
        global Pos
        global fontname, FontSize  # 添加全局字体变量
    
        Pos = (pos_x_ctrl.GetValue(), pos_y_ctrl.GetValue())
        frame.SetSize((width_ctrl.GetValue(), height_ctrl.GetValue()))
        frame.SetPosition(Pos)
    
        # 更新字体设置
        fontname = font_choice.GetStringSelection()
        FontSize = font_size_ctrl.GetValue()
        
        # 更新配置
        config['default_port'] = port_ctrl.GetValue()
        config['auto_open_browser'] = auto_open_browser.GetValue()
        config['window_pos'] = Pos
        config['window_size'] = [width_ctrl.GetValue(), height_ctrl.GetValue()]
        config['font_name'] = fontname
        config['font_size'] = FontSize
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
    # 更新主窗口字体
        frame.SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
        listbook.SetFont(wx.Font(ListButtonSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
        
        wx.MessageBox("设置已保存", "提示", wx.OK | wx.ICON_INFORMATION)
    
    save_button = wx.Button(window, label="保存设置", pos=(10, 250))
    save_button.Bind(wx.EVT_BUTTON, on_save_config)
        
    save_button_2 = wx.Button(port_panel, label="保存设置", pos=(10, 350))
    save_button_2.Bind(wx.EVT_BUTTON, on_save_config)
    
    wx.StaticText(file_panel, label="当前下载路径:", pos=(10, 10))
    path_text = wx.TextCtrl(file_panel, value=dirs, pos=(10, 30), size=(250, -1))
    
    def on_browse(event):
        dialog = wx.DirDialog(file_panel, "选择下载文件夹", 
                            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dialog.ShowModal() == wx.ID_OK:
            new_path = dialog.GetPath()
            path_text.SetValue(new_path)
            
            global dirs
            dirs = new_path + "\\"
          
            with open(target_folder + "\dir.txt", "w") as f:
                f.write(dirs)
            
        dialog.Destroy()
    
    browse_button = wx.Button(file_panel, label="浏览...", pos=(10, 70))
    link_to_2 = wx.Button(file_panel, label="检查文件路径",
                             pos=(60, 70),style=wx.BORDER_NONE,size=(140,30))
    link_to_2.SetForegroundColour(wx.Colour(0, 0, 255))  
    link_to_2.SetBackgroundColour(wx.Colour(249, 249, 249)) 
    link_to_2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    link_to_2.SetCursor(wx.Cursor(wx.CURSOR_HAND)) 
    link_to_2.Bind(wx.EVT_BUTTON, on_go_to_file)  
    browse_button.Bind(wx.EVT_BUTTON, on_browse)
    
    wx.StaticText(storage_panel, label="临时文件大小:", pos=(10, 10))
    temp_size_text = wx.StaticText(storage_panel, label="", pos=(120, 10))
    
    def update_temp_size():
        temp_path = os.path.join(dirs, "temp")
        if os.path.exists(temp_path):
            total_size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                           for dirpath, dirnames, filenames in os.walk(temp_path) 
                           for filename in filenames)
            temp_size_text.SetLabel(f"{total_size / 1024 / 1024:.2f} MB")
        else:
            temp_size_text.SetLabel("0 MB")
    

    update_temp_size()
    
    def on_clear_temp(event):
        global dirs
        temp_path = os.path.join(dirs, "temp")
        if os.path.exists(temp_path):
            for root, dirs, files in os.walk(temp_path):
                for file in files:
                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass
            wx.MessageBox("临时文件已清空", "提示", wx.OK | wx.ICON_INFORMATION)
            sys.exit()
        else:
            wx.MessageBox("临时文件夹不存在", "提示", wx.OK | wx.ICON_INFORMATION)
    
    temp_path = os.path.join(dirs, "temp")
    if os.path.exists(temp_path):
        total_size = sum(os.path.getsize(os.path.join(dirpath, filename)) 
                        for dirpath, dirnames, filenames in os.walk(temp_path) 
                        for filename in filenames)
    if total_size > 0:
        
        clear_button = wx.Button(storage_panel, label="清空临时文件", pos=(10, 40))
        clear_button.Bind(wx.EVT_BUTTON, on_clear_temp)
    else:
        clear_button = wx.Button(storage_panel, label="清空临时文件", pos=(10, 40))
        clear_button.Disable()
    wx.StaticText(storage_panel,label="临时文件时多线程下载时产生的未被删除的分块，可\n以清楚，请确保下载完毕后再清空。清空完毕后将自\n动退出",pos=(0,100))
    def on_clear_history(event):
        history_path = os.path.join(target_folder, "history.json")
        if os.path.exists(history_path):
            os.remove(history_path)
            wx.MessageBox("下载记录已清除", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("没有下载记录", "提示", wx.OK | wx.ICON_INFORMATION)

    clear_history_button = wx.Button(storage_panel, label="清除下载记录", pos=(10, 160))
    clear_history_button.Bind(wx.EVT_BUTTON, on_clear_history)
    wx.StaticText(manage_panel, label="暂未开发", pos=(10, 10))



    notebook.AddPage(window, "窗口")
    notebook.AddPage(file_panel, "文件")
    notebook.AddPage(storage_panel, "存储")
    notebook.AddPage(manage_panel, "下载")
    notebook.AddPage(port_panel, "端口")
    


    options_window.Show()




def on_go_to_file(event):
        

    if os.path.isdir(dirs):
        os.startfile(dirs) 

def on_go_to_advanced(event):
    global listbook
   
    listbook.ChangeSelection(1)
def url3(frame, event):
    pass

def on_download_button(event):
    global url_text_1, filename_text_1, dirs
    url = url_text_1.GetValue()
    filename = filename_text_1.GetValue()
    
  
    history_path = os.path.join(target_folder, "history.json")
    history = []
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append({
        "url": url,
        "filename": filename,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    
  
    CommanDownload.download_file(url, dirs+filename)
    print(f"URL: {url}, 文件名: {filename}")
    frame.SetStatusText("")

def thread_download_button(event):
    global url_text, filename_text, thread_choice, packet_size_choice,dirs
    url = url_text.GetValue()
    filename = filename_text.GetValue()
    
 
    history_path = os.path.join(target_folder, "history.json")
    history = []
    if os.path.exists(history_path):
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append({
        "url": url,
        "filename": filename,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    
    with open(history_path, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=4)
    

    packet_size = int(packet_size_choice.GetStringSelection())
    MultiThreadedDownloadFunction.main(
        url, 
        filename, 
        packet_size * 1024 * 1024, 
        int(thread_choice.GetStringSelection()),
        3000
    )

def on_help_button(event):
    wx.MessageBox("请输入要下载的文件的URL和保存的文件名，然后点击开始下载。\n若要下载大文件，请尝试“高级下载”", "帮助", wx.OK | wx.ICON_INFORMATION)
    

def on_download_enter(frame, event):
    pass

def on_help_enter(frame, event):
    pass

def on_url_enter(frame, event):
    pass

def on_url_enter_2(frame, event):
    pass

def on_filename_enter(frame, event):
    pass

def on_leave(frame, event):
    global vision
    

def on_thread_enter(frame, event):
    pass

def on_packet_size_enter(frame, event):
    pass






##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################



##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################
##########################################################################







def main():
    global url_text_1, filename_text_1
    global url_text, filename_text, thread_choice, packet_size_choice, download_button_2
    global listbook
    global url_text_analyze
    global listbook, panel5 
    app = wx.App()
    il = wx.ImageList(32,32)
    bmp1 = wx.Bitmap('icons/path_to_icon1.png')
    
    bmp2 = wx.Bitmap('icons/path_to_icon2.png')
    bmp3 = wx.Bitmap('icons/path_to_icon3.png')
    bmp4 = wx.Bitmap('icons/path_to_icon4.png')
    bmp5 = wx.Bitmap('icons/path_to_icon5.png')
    bmp6 = wx.Bitmap('icons/path_to_icon6.png')
    bmp7 = wx.Bitmap('icons/path_to_icon7.png')
    il.Add(bmp1)
    il.Add(bmp2)
    il.Add(bmp3)
    il.Add(bmp4)
    il.Add(bmp5)
    il.Add(bmp6)
    il.Add(bmp7)

    


    global frame 
    frame = wx.Frame(None, title="Advanced Network Toolset(ANT)", size=windowPos) 
   
        
  
    
    frame.SetBackgroundColour(wx.Colour(200, 200, 200))
    listbook = wx.Listbook(frame, style=wx.LB_LEFT)
   
    listbook.SetBackgroundColour(wx.Colour(200, 200, 200))
    listbook.AssignImageList(il)
    listbook.SetFont(wx.Font(ListButtonSize, wx.FONTFAMILY_DEFAULT, 
                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                  faceName=fontname))

    panel1 = wx.Panel(listbook)
    panel2 = wx.Panel(listbook)
    panel3 = wx.Panel(listbook)
    panel4 = wx.Panel(listbook)
    panel5 = wx.Panel(listbook)
    panel6 = wx.Panel(listbook)
    panel7 = wx.Panel(listbook)
    panel1.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel2.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel3.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel4.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel5.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel6.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel7.SetBackgroundColour(wx.Colour(255, 255, 255))
    listbook.AddPage(panel1, "普通下载", imageId=0)
    listbook.AddPage(panel2, "高级下载", imageId=1)
    listbook.AddPage(panel3, "分析网页", imageId=2)
    listbook.AddPage(panel6, "转发文件", imageId=5)
    listbook.AddPage(panel7, "内网聊天", imageId=6)
    listbook.AddPage(panel5, "历史记录", imageId=4)
    listbook.AddPage(panel4, "关于...", imageId=3)
    init_chat_ui(panel7)
    
    

    url_label_1 = wx.StaticText(panel1, label="URL:", pos=(10, 20))
    url_label_1.SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    url_text_1 = wx.TextCtrl(panel1, pos=(120, 20), size=Size)
    url_text_1.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_url_enter(frame, event))
    url_text_1.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    filename_label_1 = wx.StaticText(panel1, label="文件名:", pos=(10, 70)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, 
                         wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                         faceName=fontname))
    filename_text_1 = wx.TextCtrl(panel1, pos=(120, 70), size=Size)
    filename_text_1.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_filename_enter(frame, event))
    filename_text_1.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    download_button = wx.Button(panel1, label="开始下载", pos=(10, 120), size=SizeButton)
    download_button.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    download_button.Bind(wx.EVT_BUTTON, on_download_button)
    download_button.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_download_enter(frame, event))
    download_button.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    help_button = wx.Button(panel1, label="帮助", pos=(170, 120), size=SizeButton)
    help_button.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    help_button.Bind(wx.EVT_BUTTON, on_help_button)
    help_button.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_help_enter(frame, event))
    help_button.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    
    link_to_1 = wx.Button(panel1, label="若要下载大文件或从较慢的网页下载文件，请转到高级下载",
                             pos=(20, windowPos[1]-90),style=wx.BORDER_NONE,size=(335,30))
    link_to_1.SetForegroundColour(wx.Colour(0, 0, 255))  
    link_to_1.SetBackgroundColour(wx.Colour(255, 255, 255)) 
    link_to_1.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    link_to_1.SetCursor(wx.Cursor(wx.CURSOR_HAND)) 
    link_to_1.Bind(wx.EVT_BUTTON, on_go_to_advanced) 

        
    link_to_2 = wx.Button(panel1, label="打开下载文件路径",
                             pos=(Size[0]+120 , 70),style=wx.BORDER_NONE,size=(140,30))
    link_to_2.SetForegroundColour(wx.Colour(0, 0, 255))  
    link_to_2.SetBackgroundColour(wx.Colour(255, 255, 255)) 
    link_to_2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    link_to_2.SetCursor(wx.Cursor(wx.CURSOR_HAND))  
    link_to_2.Bind(wx.EVT_BUTTON, on_go_to_file)  

    




    url_label = wx.StaticText(panel2, label="URL:", pos=(10, 20)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    url_text = wx.TextCtrl(panel2, pos=(120, 20), size=Size)
    url_text.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_url_enter_2(frame, event))
    url_text.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    filename_label = wx.StaticText(panel2, label="文件名:", pos=(10, 70)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    filename_text = wx.TextCtrl(panel2, pos=(120, 70), size=Size)
    filename_text.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_filename_enter(frame, event))
    filename_text.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    thread_label = wx.StaticText(panel2, label="线程数:", pos=(10, 120)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    thread_choice = wx.Choice(panel2, pos=(120, 120), size=Size,choices=[str(i) for i in range(1, 17)]) 
    thread_choice.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_thread_enter(frame, event))
    thread_choice.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    packet_size_label = wx.StaticText(panel2, label="分包大小(MB):", pos=(10, 170)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    packet_size_choice = wx.Choice(panel2, pos=(190, 170),  size=Size,choices=[str(i) for i in range(1, 101)])  
    packet_size_choice.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_packet_size_enter(frame, event))
    packet_size_choice.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    download_button_2 = wx.Button(panel2, label="开始下载", pos=(10, 220), size=SizeButton)
    download_button_2.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    download_button_2.Bind(wx.EVT_BUTTON, thread_download_button)
    download_button_2.Bind(wx.EVT_ENTER_WINDOW, lambda event: on_download_enter(frame, event))
    download_button_2.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))



    link_to_2 = wx.Button(panel2, label="打开下载文件路径",
                             pos=(Size[0]+120 , 70),style=wx.BORDER_NONE,size=(140,30))
    link_to_2.SetForegroundColour(wx.Colour(0, 0, 255)) 
    link_to_2.SetBackgroundColour(wx.Colour(255, 255, 255)) 
    link_to_2.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    link_to_2.SetCursor(wx.Cursor(wx.CURSOR_HAND)) 
    link_to_2.Bind(wx.EVT_BUTTON, on_go_to_file) 




    # 分析网页面板
    url_label_analyze = wx.StaticText(panel3, label="URL:", pos=(10, 20)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    url_text_analyze = wx.TextCtrl(panel3, pos=(120, 20), size=Size)
    url_text_analyze.Bind(wx.EVT_ENTER_WINDOW, lambda event: url3(frame, event))
    url_text_analyze.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    analyze_button = wx.Button(panel3, label="分析", pos=(10, 70), size=SizeButton)
    analyze_button.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    analyze_button.Bind(wx.EVT_ENTER_WINDOW, lambda event: frame.SetStatusText("点击分析网页"))
    analyze_button.Bind(wx.EVT_BUTTON, on_analyze)
    #关于
    wx.StaticText(panel4, label="关于软件", pos=(10, 0)).SetFont(wx.Font(FontSize+10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    wx.StaticText(panel4, label="作者:YJY_\n版本:"+vision+"\n文件保存路径: "+dirs+"\n默认端口"+str(config.get('default_port', 1524)), pos=(10, 70)).SetFont(wx.Font(FontSize-7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))

    # 添加更新服务器链接
    update_link = wx.Button(panel4, label="更新服务器", 
                          pos=(0, 150), style=wx.BORDER_NONE, size=(100, 30))
    update_link.SetForegroundColour(wx.Colour(0, 0, 255))
    update_link.SetBackgroundColour(wx.Colour(255, 255, 255))
    update_link.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    update_link.SetCursor(wx.Cursor(wx.CURSOR_HAND))
    def on_update_link(event):
        import webbrowser
        webbrowser.open("https://yjymain.rth1.xyz/")
    update_link.Bind(wx.EVT_BUTTON, on_update_link)

    download_button_op = wx.Button(panel4, label="首选项", pos=(170, 10), size=SizeButton)
    download_button_op.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    download_button_op.Bind(wx.EVT_BUTTON, options)


    """创建图形化界面"""
    

    
    # 控件
    port_label = wx.StaticText(panel6,label="端口号:", pos=(10, 20)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    port_text = wx.TextCtrl(panel6,pos=(110, 20), size=(100, -1))
    port_text.SetValue(str(config.get('default_port', 1524)))
    
    file_label = wx.StaticText(panel6,label="文件路径:", pos=(10, 60)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    file_text = wx.TextCtrl(panel6,pos=(110, 60), size=(200, -1))
    
    browse_button = wx.Button(panel6,label="浏览...", pos=(340, 60), size=(80, -1))
    
    log_text = wx.TextCtrl(panel6, pos=(10, 100), size=(530, 170), 
                        style=wx.TE_MULTILINE|wx.TE_READONLY)
    log_text.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, 
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                            faceName=fontname))
    start_button = wx.Button(panel6, label="启动", pos=(10, 270), size=(80, -1))
    stop_button = wx.Button(panel6, label="停止", pos=(100, 270), size=(80, -1))
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
        
        if not os.path.exists(file_path):
            wx.MessageBox("文件不存在！", "错误", wx.OK | wx.ICON_ERROR)
            return
        print(file_path)

            
        # 添加到历史记录
        history_path = os.path.join(target_folder, "history.json")
        history = []
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            
            "url": port,
            "filename": os.path.basename(file_path),
            "time": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
        
        start_button.Disable()
        stop_button.Enable()
        
        server_thread = threading.Thread(
            target=TPort.start_file_server,
            args=(port, file_path, os.path.dirname(file_path), lambda msg: wx.CallAfter(log_text.AppendText, msg)),
            daemon=True
        )
        server_thread.start()
        if config.get('auto_open_browser', True):
            import webbrowser
            webbrowser.open(f"http://localhost:{port}")
    
    def on_stop(event):
        TPort.stop_file_server(lambda msg: wx.CallAfter(log_text.AppendText, msg))
        start_button.Enable()
        stop_button.Disable()
    
    # 绑定事件
    browse_button.Bind(wx.EVT_BUTTON, on_browse)
    start_button.Bind(wx.EVT_BUTTON, on_start)
    stop_button.Bind(wx.EVT_BUTTON, on_stop)




    def load_history():
        history_path = os.path.join(target_folder, "history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    history_list = wx.ListCtrl(panel5, style=wx.LC_REPORT|wx.LC_SINGLE_SEL, pos=(10, 10), size=(windowPos[0]-170,windowPos[1]-130))
    history_list.InsertColumn(0, 'URL', width=100)
    history_list.InsertColumn(1, '文件', width=400)
    history_list.InsertColumn(2, '时间', width=150)
    for record in load_history():
        history_list.Append([record['url'], record['filename'], record['time']])
    def on_copy_url(event):
        selected = history_list.GetFirstSelected()
        if selected != -1:
            url = history_list.GetItem(selected, 0).GetText()
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(wx.TextDataObject(url))
                wx.TheClipboard.Close()
                wx.MessageBox("URL已复制到剪贴板", "提示", wx.OK | wx.ICON_INFORMATION)
            else:
                wx.MessageBox("无法访问剪贴板", "错误", wx.OK | wx.ICON_ERROR)
        else:
            wx.MessageBox("请先选择一条记录", "提示", wx.OK | wx.ICON_INFORMATION)

    copy_button = wx.Button(panel5, label="复制URL", pos=(10, windowPos[1]-100), size=(100, 30))
    copy_button.Bind(wx.EVT_BUTTON, on_copy_url)

    

    


    frame.Show()


    
    

    app.MainLoop()

main()
