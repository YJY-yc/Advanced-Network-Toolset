
vision = "3.5.1.8"


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

import wx.adv
import DatchDownload 
import requests,time,wx
import webbrowser
from bs4 import BeautifulSoup
from update import *










url_text_1, filename_text_1 = "", ""

listbook=None
url_text_analyze=None
time_ctrl=None


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
    'window_size': [800, 550]  
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





def init_download_tab(panel):
 
    vbox = wx.BoxSizer(wx.VERTICAL)
    

    hbox0 = wx.BoxSizer(wx.HORIZONTAL)
    import_btn = wx.Button(panel, label="导入网址文件")
    hbox0.Add(import_btn, 0, wx.ALL|wx.CENTER, 5)
    vbox.Add(hbox0, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
    
  
    hbox3 = wx.BoxSizer(wx.HORIZONTAL)
    main_site_label = wx.StaticText(panel, label="主网站:")
    main_site_text = wx.TextCtrl(panel)
    hbox3.Add(main_site_label, 0, wx.ALL|wx.CENTER, 5)
    hbox3.Add(main_site_text, 1, wx.ALL|wx.EXPAND, 5)
    vbox.Add(hbox3, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
    

    hbox2 = wx.BoxSizer(wx.HORIZONTAL)
    thread_label = wx.StaticText(panel, label="线程数:")
    thread_spin = wx.SpinCtrl(panel, min=1, max=10, initial=4)
    hbox2.Add(thread_label, 0, wx.ALL|wx.CENTER, 5)
    hbox2.Add(thread_spin, 1, wx.ALL|wx.EXPAND, 5)
    vbox.Add(hbox2, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
    
 
    undownloaded_list = wx.ListBox(panel, style=wx.LB_SINGLE)
    vbox.Add(undownloaded_list, 1, wx.ALL|wx.EXPAND, 10)
    

    download_btn = wx.Button(panel, label="开始下载")
    vbox.Add(download_btn, 0, wx.ALL|wx.CENTER, 10)
    

    import_btn.Bind(wx.EVT_BUTTON, lambda event: on_import(panel, undownloaded_list))
    download_btn.Bind(wx.EVT_BUTTON, lambda event: DatchDownload.create_download_window(
        panel, 
        panel.urls, 
        thread_spin.GetValue(), 
        main_site_text.GetValue(), 
        DatchDownload.get_download_dir()
    ))

    panel.urls = []
    
    panel.SetSizer(vbox)

def on_import(panel, undownloaded_list):
    with wx.FileDialog(panel, "选择网址文件", wildcard="Text files (*.txt)|*.txt",
                     style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return []
        
        path = fileDialog.GetPath()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                wx.MessageBox(f"成功导入 {len(urls)} 个网址", "提示", wx.OK|wx.ICON_INFORMATION)
                undownloaded_list.Set(urls)
                panel.urls = urls
                return urls
        except Exception as e:
            wx.MessageBox(f"导入文件失败: {str(e)}", "错误", wx.OK|wx.ICON_ERROR)
            return []




def init_chat_ui(panel):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        ip_ctrl = wx.TextCtrl(panel, value="127.0.0.1")
        port_ctrl = wx.TextCtrl(panel, value="5000")
        disconnect_btn = wx.Button(panel, label="断开连接")
        connect_btn = wx.Button(panel, label="连接到...")
        start_btn = wx.Button(panel, label="启动服务")
        hbox1.Add(ip_ctrl, 1, wx.EXPAND|wx.ALL, 5)
        hbox1.Add(port_ctrl, 0, wx.EXPAND|wx.ALL, 5)
        hbox1.Add(connect_btn, 0, wx.ALL, 5)
        hbox1.Add(start_btn, 0, wx.ALL, 5)
        hbox1.Add(disconnect_btn, 0, wx.ALL, 5)
        
        chat_list = wx.ListBox(panel, style=wx.LB_SINGLE, size=(400, 200))
        def on_right_click(event):
            menu = wx.Menu()
            copy_item = menu.Append(wx.ID_ANY, "复制")
            delete_item = menu.Append(wx.ID_ANY, "删除")
            
           
            def on_copy(event):
                selection = chat_list.GetSelection()
                if selection != wx.NOT_FOUND:
                    text = chat_list.GetString(selection)
                    if wx.TheClipboard.Open():
                        wx.TheClipboard.SetData(wx.TextDataObject(text))
                        wx.TheClipboard.Close()
            
            def on_delete(event):
                selection = chat_list.GetSelection()
                if selection != wx.NOT_FOUND:
                    chat_list.Delete(selection)
            
            chat_list.Bind(wx.EVT_MENU, on_copy, copy_item)
            chat_list.Bind(wx.EVT_MENU, on_delete, delete_item)
            
            chat_list.PopupMenu(menu)
            menu.Destroy()
        chat_list.Bind(wx.EVT_CONTEXT_MENU, on_right_click)
       
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        msg_ctrl = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        send_btn = wx.Button(panel, label="发送")
        hbox2.Add(msg_ctrl, 1, wx.EXPAND|wx.ALL, 5)
        hbox2.Add(send_btn, 0, wx.ALL, 5)

        disconnect_btn.Disable()
        
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
        
        msg_display = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        vbox.Add(hbox3, 0, wx.EXPAND|wx.ALL, 5)
        vbox.Add(msg_display, 1, wx.EXPAND|wx.ALL, 5)
        
       
        def on_show_message(event):
            selection = chat_list.GetSelection()
            if selection != wx.NOT_FOUND:
                msg = chat_list.GetString(selection)
                msg_display.SetValue(msg)
            else:
                wx.MessageBox("请先选择一条消息", "提示", wx.OK | wx.ICON_INFORMATION)
        
        show_btn.Bind(wx.EVT_BUTTON, on_show_message)
        
        controls = {
        'ip_ctrl': ip_ctrl,
        'port_ctrl': port_ctrl,
        'connect_btn': connect_btn,
        'start_btn': start_btn,
        'chat_list': chat_list,
        'msg_ctrl': msg_ctrl,
        'send_btn': send_btn,
        'msg_type': msg_type,
        'disconnect_btn': disconnect_btn, 
        'sock': None,
        'msg_display': msg_display,
        'server_socket': None,
        'toast': Notification(
            app_id="内网聊天",
            title="新消息",
            duration="short"
        )  
        }
        def on_export_chat(event):
            with wx.FileDialog(frame, "导出聊天记录", wildcard="Text files (*.txt)|*.txt",
                            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

                if fileDialog.ShowModal() == wx.ID_CANCEL:
                    return     

              
                pathname = fileDialog.GetPath()
                try:
                    with open(pathname, 'w', encoding='utf-8') as f:
                        for i in range(chat_list.GetCount()):
                            f.write(chat_list.GetString(i) + '\n')
                    wx.MessageBox(f"聊天记录已成功导出到 {pathname}", "成功", wx.OK | wx.ICON_INFORMATION)
                except IOError:
                    wx.MessageBox(f"无法保存文件 {pathname}", "错误", wx.OK | wx.ICON_ERROR)

        export_btn.Bind(wx.EVT_BUTTON, on_export_chat)
        def on_disconnect(event):
            if 'sock' in controls and controls['sock']:
                try:
                    controls['sock'].close()
                    controls['sock'] = None  
                except:
                    pass
            if 'original_sock' in controls and controls['original_sock']:
                try:
                    controls['original_sock'].close()
                    controls['original_sock'] = None  
                except:
                    pass
            controls['ip_ctrl'].Enable()
            controls['connect_btn'].Enable()
            controls['start_btn'].Enable()
            controls['ip_ctrl'].SetValue("127.0.0.1")
            controls['port_ctrl'].SetValue(str(int(controls['port_ctrl'].GetValue()) + 2))
            controls['msg_ctrl'].Enable()
            controls['send_btn'].Enable()
            wx.MessageBox("已断开所有连接", "提示", wx.OK | wx.ICON_INFORMATION)
           
        disconnect_btn.Bind(wx.EVT_BUTTON, on_disconnect)
        connect_btn.Bind(wx.EVT_BUTTON, lambda event: on_connect(event, controls, controls['sock'], controls['server_socket']))
        start_btn.Bind(wx.EVT_BUTTON, lambda event: on_start_server(event, controls))
        send_btn.Bind(wx.EVT_BUTTON, lambda event: on_send(event, controls, controls['sock'], controls['toast']))
        msg_ctrl.Bind(wx.EVT_TEXT_ENTER, lambda event: on_send(event, controls, controls['sock'], controls['toast']))



username_ctrl,password_ctrl=None,None

check=None

def on_analyze(event):
    global url_text_analyze,time_ctrl,check
    head="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    try:
        header_path = os.path.join(target_folder, "Head.ANT")
        if os.path.exists(header_path):
            with open(header_path, 'r', encoding='utf-8') as f:
                head=f.read()
    except:
        head="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"

    
    analyze.on_analyze_button(url_text_analyze.GetValue(), head,int(time_ctrl.GetValue()),check.GetValue())

def options(event):
    global dirs
    global Pos
    Pos = config.get('window_pos', (100, 20))  
    options_window = wx.Frame(None, title="首选项", size=(400, 500))



    def on_close(event):
        options_window.Destroy()
        event.Skip()
    
    options_window.Bind(wx.EVT_CLOSE, on_close)
    notebook = wx.Notebook(options_window,pos=(0,0))
    window = wx.Panel(notebook)
    file_panel = wx.Panel(notebook)
    storage_panel = wx.Panel(notebook)



    port_panel = wx.Panel(notebook)
    header_panel = wx.Panel(notebook) 

    wx.StaticText(header_panel, label="请求头User-Agent设置:", pos=(10, 10))
    header_text = wx.TextCtrl(header_panel, pos=(10, 30), size=(350, 100), 
                            style=wx.TE_MULTILINE)

    header_path = os.path.join(target_folder, "Head.ANT")
    if os.path.exists(header_path):
        with open(header_path, 'r', encoding='utf-8') as f:
            header_text.SetValue(f.read())

  
    wx.StaticText(header_panel, label="默认请求头User-Agent:", pos=(10, 140))
    default_header_text = wx.TextCtrl(header_panel, pos=(10, 160), size=(350, 100), 
                                    style=wx.TE_MULTILINE|wx.TE_READONLY)
    default_header_text.SetValue("""Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36""")

    def apply_default_header():
        if wx.MessageBox("确定要用默认请求头覆盖当前请求头吗？", "确认", 
                       wx.YES_NO|wx.ICON_QUESTION) == wx.YES:
            header_text.SetValue(default_header_text.GetValue())
            wx.MessageBox("默认请求头已应用", "提示", wx.OK | wx.ICON_INFORMATION)

    apply_header_btn = wx.Button(header_panel, label="应用默认请求头", pos=(10, 270))
    apply_header_btn.Bind(wx.EVT_BUTTON, lambda e: apply_default_header())

    def save_headers():
        with open(header_path, 'w', encoding='utf-8') as f:
            f.write(header_text.GetValue())
        wx.MessageBox("请求头已保存", "提示", wx.OK | wx.ICON_INFORMATION)

    save_header_btn = wx.Button(header_panel, label="保存请求头", pos=(10, 310))
    save_header_btn.Bind(wx.EVT_BUTTON, lambda e: save_headers())








    wx.StaticText(port_panel, label="默认端口:", pos=(10, 0))
    port_ctrl = wx.SpinCtrl(port_panel, value=str(config.get('default_port', 1524)), 
                          pos=(100, 0), min=1024, max=65535)
    
    
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
    win_ctrl = wx.SpinCtrl(window, value=str(frame.GetSize().GetWidth()), pos=(100, 200), min=400, max=1920)

    winht_ctrl = wx.SpinCtrl(window, value=str(frame.GetSize().GetHeight()), pos=(170, 200), min=300, max=1080)

    def on_save_config(event):
        global Pos
        global fontname, FontSize  
    
        Pos = (pos_x_ctrl.GetValue(), pos_y_ctrl.GetValue())
        frame.SetSize((win_ctrl.GetValue(), winht_ctrl.GetValue()))
        frame.SetPosition(Pos)
    
        fontname = font_choice.GetStringSelection()
        FontSize = font_size_ctrl.GetValue()
        
        config['default_port'] = port_ctrl.GetValue()
        config['auto_open_browser'] = auto_open_browser.GetValue()
        config['window_pos'] = Pos
        config['window_size'] = [win_ctrl.GetValue(), winht_ctrl.GetValue()]
        config['font_name'] = fontname
        config['font_size'] = FontSize
        config['size'] = [width_ctrl.GetValue(), height_ctrl.GetValue()]  
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
   
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
    try:
        if total_size > 0:
        
            clear_button = wx.Button(storage_panel, label="清空临时文件", pos=(10, 40))
            clear_button.Bind(wx.EVT_BUTTON, on_clear_temp)
        else:
            clear_button = wx.Button(storage_panel, label="清空临时文件", pos=(10, 40))
            clear_button.Disable()
        wx.StaticText(storage_panel,label="临时文件是多线程下载时产生的未被删除的分块，可\n以清楚，请确保下载完毕后再清空。清空完毕后将自\n动退出",pos=(0,100))
    except:
        wx.MessageBox("请设置下载目录！", "提示", wx.OK | wx.ICON_INFORMATION)
    def on_clear_history(event):
        history_path = os.path.join(target_folder, "history.json")
        if os.path.exists(history_path):
            os.remove(history_path)
            wx.MessageBox("下载记录已清除", "提示", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("没有下载记录", "提示", wx.OK | wx.ICON_INFORMATION)

    clear_history_button = wx.Button(storage_panel, label="清除下载记录", pos=(10, 160))
    clear_history_button.Bind(wx.EVT_BUTTON, on_clear_history)
   



    notebook.AddPage(window, "窗口")
    notebook.AddPage(file_panel, "文件")
    notebook.AddPage(storage_panel, "存储")
    notebook.AddPage(header_panel, "请求头")
    notebook.AddPage(port_panel, "端口")
    


    options_window.Show()
    options_window.Show()
    options_window.Raise() 
    options_window.SetFocus() 




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
    
    header_path = os.path.join(target_folder, "Head.ANT")
    if os.path.exists(header_path):
        with open(header_path, 'r', encoding='utf-8') as f:
            he=f.read()

    CommanDownload.download_file(url, dirs+filename,he)
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


def create_tray_icon():
    icon = wx.Icon('icons/path_to_icon1.png', wx.BITMAP_TYPE_PNG)
    tray = wx.adv.TaskBarIcon()
    tray.SetIcon(icon, "Advanced Network Toolset")
    

    def create_menu():
        menu = wx.Menu()
        show_item = menu.Append(wx.ID_ANY, "显示窗口")
        hid_item = menu.Append(wx.ID_ANY, "隐藏窗口")
        update_item = menu.Append(wx.ID_ANY, "检测更新")
        opt_item = menu.Append(wx.ID_ANY, "首选项")
        exit_item = menu.Append(wx.ID_EXIT, "退出")
        
    
        def on_show(event):
            frame.Show()
            frame.Raise()
            frame.Iconize(False)
        def on_exit(event):
            tray.Destroy()
            frame.Destroy()
        def on_hid(event):
            frame.Hide()
        def on_check(event):
            
            wx.CallAfter(show_update_dialog, "V"+vision)
        def opt_check(event):
            options(event)
        tray.Bind(wx.EVT_MENU, on_show, show_item)
        tray.Bind(wx.EVT_MENU, on_exit, exit_item)
        tray.Bind(wx.EVT_MENU, on_hid, hid_item)
        tray.Bind(wx.EVT_MENU, on_check, update_item)
        tray.Bind(wx.EVT_MENU, opt_check,opt_item)
        return menu
    

    def on_tray_double_click(event):
        frame.Show()
        frame.Raise()
        frame.Iconize(False)
        
    tray.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, on_tray_double_click)
    
 
    def on_right_click(event):
        tray.PopupMenu(create_menu())
        
    tray.Bind(wx.adv.EVT_TASKBAR_RIGHT_UP, on_right_click)
    return tray

def main():
    global url_text_1, filename_text_1,check
    global url_text, filename_text, thread_choice, packet_size_choice, download_button_2
    global listbook
    global url_text_analyze
    global listbook, panel5 
    global username_ctrl,password_ctrl
    global time_ctrl
    app = wx.App()
    il = wx.ImageList(32,32)
    bmp1 = wx.Bitmap('icons/path_to_icon1.png')
    bmp2 = wx.Bitmap('icons/path_to_icon2.png')
    bmp3 = wx.Bitmap('icons/path_to_icon3.png')
    bmp4 = wx.Bitmap('icons/path_to_icon4.png')
    bmp5 = wx.Bitmap('icons/path_to_icon5.png')
    bmp6 = wx.Bitmap('icons/path_to_icon6.png')
    bmp7 = wx.Bitmap('icons/path_to_icon7.png')
    bmp8 = wx.Bitmap('icons/home.png') 
    bmp9 = wx.Bitmap('icons/arrow.png')  
    bmp10 = wx.Bitmap('icons/path_to_icon8.png')
    il.Add(bmp1)
    il.Add(bmp2)
    il.Add(bmp3)
    il.Add(bmp4)
    il.Add(bmp5)
    il.Add(bmp6)
    il.Add(bmp7)
    il.Add(bmp8)
    il.Add(bmp9)
    il.Add(bmp10)
    
    
    icon = wx.Icon('icons/path_to_icon1.png', wx.BITMAP_TYPE_PNG)
    tray = wx.adv.TaskBarIcon()
    tray.SetIcon(icon, "Advanced Network Toolset")

    global frame 
    frame = wx.Frame(None, title="Advanced Network Toolset(ANT)", size=windowPos) 
   
    

    def on_close(event):
        frame.Hide()
        
    frame.Bind(wx.EVT_CLOSE, on_close)
    tray = create_tray_icon()
    
    frame.SetBackgroundColour(wx.Colour(200, 200, 200))
    listbook = wx.Listbook(frame, style=wx.LB_LEFT)
   
    listbook.SetBackgroundColour(wx.Colour(200, 200, 200))
    listbook.AssignImageList(il)
    listbook.SetFont(wx.Font(ListButtonSize, wx.FONTFAMILY_DEFAULT, 
                  wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                  faceName=fontname))
    panel0 = wx.Panel(listbook)
    panel1 = wx.Panel(listbook)
    panel2 = wx.Panel(listbook)
    panel3 = wx.Panel(listbook)
    panel4 = wx.Panel(listbook)
    panel5 = wx.Panel(listbook)
    panel6 = wx.Panel(listbook)
    panel7 = wx.Panel(listbook)
    panel8 = wx.Panel(listbook)
    panel0.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel1.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel2.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel3.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel4.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel5.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel6.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel7.SetBackgroundColour(wx.Colour(255, 255, 255))
    panel8.SetBackgroundColour(wx.Colour(255, 255, 255))
    listbook.AddPage(panel0, "主页", imageId=7)
    listbook.AddPage(panel1, "普通下载", imageId=0)
    listbook.AddPage(panel2, "高级下载", imageId=1)
    listbook.AddPage(panel8, "批量下载", imageId=9)
    listbook.AddPage(panel3, "分析网页", imageId=2)
    listbook.AddPage(panel6, "转发文件", imageId=5)
    listbook.AddPage(panel7, "内网聊天", imageId=6)
    listbook.AddPage(panel5, "历史记录", imageId=4)
    listbook.AddPage(panel4, "关于...", imageId=3)
    
    init_chat_ui(panel7)
    
    init_download_tab(panel8)

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


    
    url_label_analyze = wx.StaticText(panel3, label="URL:", pos=(10, 20)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    url_text_analyze = wx.TextCtrl(panel3, pos=(120, 20), size=Size)
    url_text_analyze.Bind(wx.EVT_ENTER_WINDOW, lambda event: url3(frame, event))
    url_text_analyze.Bind(wx.EVT_LEAVE_WINDOW, lambda event: on_leave(frame, event))

    analyze_button = wx.Button(panel3, label="分析", pos=(10, 160), size=SizeButton)
    analyze_button.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    analyze_button.Bind(wx.EVT_ENTER_WINDOW, lambda event: frame.SetStatusText)
    analyze_button.Bind(wx.EVT_BUTTON, on_analyze)

    check=wx.CheckBox(panel3, label="渲染源码（更慢）", 
                                  pos=(10, 120))
    wx.StaticText(panel3, label="超时时间:", pos=(10, 70))
    time_ctrl = wx.SpinCtrl(panel3, value="5", 
                          pos=(120, 70), min=1, max=120)

    
    wx.StaticText(panel4, label="关于软件", pos=(10, 0)).SetFont(wx.Font(FontSize+10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    wx.StaticText(panel4, label="作者:YJY_\n版本:"+vision+"\n文件保存路径: "+dirs+"\n默认端口"+str(config.get('default_port', 1524)), pos=(10, 70)).SetFont(wx.Font(FontSize-7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))

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




    port_label = wx.StaticText(panel6,label="端口号:", pos=(10, 20)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    port_text = wx.TextCtrl(panel6,pos=(110, 20), size=(100, -1))
    port_text.SetValue(str(config.get('default_port', 1524)))
    
    file_label = wx.StaticText(panel6,label="文件路径:", pos=(10, 60)).SetFont(wx.Font(FontSize, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    file_text = wx.TextCtrl(panel6,pos=(130, 60), size=(200, -1))
    
    browse_button = wx.Button(panel6,label="浏览...", pos=(360, 60), size=(80, -1))
    
    log_text = wx.TextCtrl(panel6, pos=(10, 100), size=(530, 170), 
                        style=wx.TE_MULTILINE|wx.TE_READONLY)
    log_text.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, 
                            wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, 
                            faceName=fontname))
    start_button = wx.Button(panel6, label="启动", pos=(10, 270), size=(80, -1))
    stop_button = wx.Button(panel6, label="停止", pos=(100, 270), size=(80, -1))
    stop_button.Disable()
    
   



    def create_home_button(label, target_page, icon_idx):
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        button = wx.Button(panel0, label=label, size=(200, 35))
        button.SetFont(wx.Font(FontSize-4, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
        button.SetBackgroundColour(wx.Colour(50, 200, 200))
       
        icon = wx.StaticBitmap(panel0, bitmap=il.GetBitmap(icon_idx))
        arrow = wx.StaticBitmap(panel0, bitmap=il.GetBitmap(8)) 
        
        sizer.Add(icon, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizer.Add(button, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(arrow, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        
        button.Bind(wx.EVT_BUTTON, lambda e: listbook.ChangeSelection(target_page))
        return sizer

    
    main_sizer = wx.BoxSizer(wx.VERTICAL)
    main_sizer.AddSpacer(50)
    wx.StaticText(panel0,label="主页 高级网络工具ANT", pos=(10, 0)).SetFont(wx.Font(25, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    main_sizer.Add(create_home_button("普通下载", 1, 0), 0, wx.EXPAND|wx.ALL, 0)
    main_sizer.Add(create_home_button("高级下载", 2, 1), 0, wx.EXPAND|wx.ALL,0)
    main_sizer.Add(create_home_button("批量下载", 3, 9), 0, wx.EXPAND|wx.ALL,0)
    main_sizer.Add(create_home_button("网页分析", 4, 2), 0, wx.EXPAND|wx.ALL, 0)
    main_sizer.Add(create_home_button("文件转发", 5, 5), 0, wx.EXPAND|wx.ALL, 0)
    main_sizer.Add(create_home_button("内网聊天", 6, 6), 0, wx.EXPAND|wx.ALL, 0)
    main_sizer.Add(create_home_button("历史记录", 7, 4), 0, wx.EXPAND|wx.ALL, 0)
    main_sizer.Add(create_home_button("关于软件/首选项", 8, 3), 0, wx.EXPAND|wx.ALL, 0)
    header_path = os.path.join(target_folder, "Head.ANT")
    try:
        if os.path.exists(header_path):
            with open(header_path, 'r', encoding='utf-8') as f:
                head=f.read()
            if head=="":
                wx.StaticText(panel0,label="请完成请求头设置(关于>首选项>请求头)", pos=(10, 420)).SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
        else:
            wx.StaticText(panel0,label="请完成请求头设置(关于>首选项>请求头)", pos=(10, 420)).SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    except:
        wx.StaticText(panel0,label="请完成请求头设置(关于>首选项>请求头)", pos=(10, 420)).SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=fontname))
    panel0.SetSizer(main_sizer)



    
    listbook.ChangeSelection(0)


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

        # 获取所有可用的IP地址
        import socket
        hostname = socket.gethostname()
        addrinfo = socket.getaddrinfo(hostname, None)
        
        # 显示所有IP地址
        ip_addresses = []
        for addr in addrinfo:
            ip_address = addr[4][0]
            ip_addresses.append(ip_address)
        
        if not ip_addresses:
            wx.MessageBox("无法获取IP地址", "错误", wx.OK | wx.ICON_ERROR)
            return
        
     
        ip_address = ip_addresses[-2] if len(ip_addresses) > 1 else ip_addresses[0]
        
        
        wx.CallAfter(log_text.AppendText, f"服务器启动在: {ip_address}:{port}请用此连接访问\n")
        
        history_path = os.path.join(target_folder, "history.json")
        history = []
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        
        history.append({
            "url": f"{ip_address}:{port}", 
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
        
    def on_stop(event):
        TPort.stop_file_server(lambda msg: wx.CallAfter(log_text.AppendText, msg))
        start_button.Enable()
        stop_button.Disable()
    
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
    history_list.InsertColumn(0, 'URL', width=300)
    history_list.InsertColumn(1, '文件', width=200)
    history_list.InsertColumn(2, '时间', width=150)
    
   
    def on_right_click(event):
        menu = wx.Menu()
        
        
        copy_url_item = menu.Append(wx.ID_ANY, "复制URL")
       
        copy_filename_item = menu.Append(wx.ID_ANY, "复制文件名")
      
        delete_item = menu.Append(wx.ID_ANY, "删除")
        
       
        def on_copy_url(event):
            selected = history_list.GetFirstSelected()
            if selected != -1:
                url = history_list.GetItem(selected, 0).GetText()
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(url))
                    wx.TheClipboard.Close()
        
        def on_copy_filename(event):
            selected = history_list.GetFirstSelected()
            if selected != -1:
                filename = history_list.GetItem(selected, 1).GetText()
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData(wx.TextDataObject(filename))
                    wx.TheClipboard.Close()
        
        def on_delete(event):
            selected = history_list.GetFirstSelected()
            if selected != -1:
                
                history_list.DeleteItem(selected)
                
                history = load_history()
                del history[selected]
                with open(os.path.join(target_folder, "history.json"), 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=4)
        
        history_list.Bind(wx.EVT_MENU, on_copy_url, copy_url_item)
        history_list.Bind(wx.EVT_MENU, on_copy_filename, copy_filename_item)
        history_list.Bind(wx.EVT_MENU, on_delete, delete_item)
        
        history_list.PopupMenu(menu)
        menu.Destroy()
    
    history_list.Bind(wx.EVT_CONTEXT_MENU, on_right_click)
    
    def on_resize(event):
        new_size = frame.GetSize()
        history_list.SetSize((new_size[0]-170, new_size[1]-130))
        event.Skip()
    
    frame.Bind(wx.EVT_SIZE, on_resize)

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
