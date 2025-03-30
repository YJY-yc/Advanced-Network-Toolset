import wx
import requests
import threading, os, time
from urllib.parse import urlparse
from pathlib import Path
from winotify import Notification, audio
from concurrent.futures import ThreadPoolExecutor

def get_download_dir():
    appdata_dir = os.getenv('APPDATA')
    config_path = os.path.join(appdata_dir, 'NetDownloader', 'dir.txt')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except:
        return os.path.join(os.getcwd(), "downloads")


stop_download = False
def create_download_window(parent, urls, thread_count, main_site, download_dir):
   
    download_window = wx.Frame(parent, title="下载进度", size=(400, 300))
    panel = wx.Panel(download_window)
    vbox = wx.BoxSizer(wx.VERTICAL)
    
  
    new_gauge = wx.Gauge(panel, range=100)
    new_remaining_label = wx.StaticText(panel, label="剩余项: 0")
    new_undownloaded_list = wx.ListBox(panel, style=wx.LB_SINGLE)
    new_export_btn = wx.Button(panel, label="导出未下载列表")
    
   
    vbox.Add(new_gauge, 0, wx.ALL|wx.EXPAND, 10)
    vbox.Add(new_remaining_label, 0, wx.ALL|wx.CENTER, 5)
    vbox.Add(new_undownloaded_list, 1, wx.ALL|wx.EXPAND, 10)
    

    stop_btn = wx.Button(panel, label="停止下载")
    end_and_export_btn = wx.Button(panel, label="结束并导出")
    

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    hbox.Add(new_export_btn, 0, wx.ALL|wx.CENTER, 5)
    hbox.Add(stop_btn, 0, wx.ALL|wx.CENTER, 5)
    hbox.Add(end_and_export_btn, 0, wx.ALL|wx.CENTER, 5)
    vbox.Add(hbox, 0, wx.ALL|wx.CENTER, 10)
    
  
    new_export_btn.Bind(wx.EVT_BUTTON, lambda event: on_export(download_window, new_undownloaded_list))
    
    panel.SetSizer(vbox)
    download_window.Show()
    

    stop_btn.Bind(wx.EVT_BUTTON, lambda event: on_stop(download_window))
    end_and_export_btn.Bind(wx.EVT_BUTTON, lambda event: on_end_and_export(download_window, new_undownloaded_list))
    

    threading.Thread(
        target=start_download, 
        args=(urls, thread_count, new_gauge, new_remaining_label, new_undownloaded_list, main_site, download_dir, download_window)
    ).start()

def on_end_and_export(window, undownloaded_list):
    global stop_download
    stop_download = True
    wx.CallAfter(on_export, window, undownloaded_list)
    wx.CallAfter(window.Close)
def on_stop(window):
    global stop_download
    stop_download = True
    wx.MessageBox("下载已停止", "提示", wx.OK|wx.ICON_INFORMATION)
    window.Close()
def create_download_app():
    app = wx.App(False)
    frame = wx.Frame(None, title="批量下载器", size=(600, 400))
    
    panel = wx.Panel(frame)
    vbox = wx.BoxSizer(wx.VERTICAL)
    frame.urls = []  
    
    hbox0 = wx.BoxSizer(wx.HORIZONTAL)
    import_btn = wx.Button(panel, label="导入网址文件")
    hbox0.Add(import_btn, 0, wx.ALL|wx.CENTER, 5)
    vbox.Add(hbox0, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 10)
    appdata_dir = os.getenv('APPDATA')
    config_path = os.path.join(appdata_dir, 'NetDownloader', 'dir.txt')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            download_dir = f.read().strip()
    except:
        download_dir = os.path.join(os.getcwd(), "downloads")


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


    import_btn.Bind(wx.EVT_BUTTON, lambda event: frame.urls.extend(on_import(frame, undownloaded_list)))
    
    
    download_btn.Bind(wx.EVT_BUTTON, lambda event: create_download_window(
        frame, 
        frame.urls,  
        thread_spin.GetValue(), 
        main_site_text.GetValue(), 
        download_dir
    ))
     
    panel.SetSizer(vbox)
    frame.Show()
    app.MainLoop()
def on_import(frame, undownloaded_list):
    with wx.FileDialog(frame, "选择网址文件", wildcard="Text files (*.txt)|*.txt",
                     style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        
        path = fileDialog.GetPath()
        try:
            with open(path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
                wx.MessageBox(f"成功导入 {len(urls)} 个网址", "提示", wx.OK|wx.ICON_INFORMATION)
                undownloaded_list.Set(urls) 
                return urls
        except Exception as e:
            wx.MessageBox(f"导入文件失败: {str(e)}", "错误", wx.OK|wx.ICON_ERROR)
            return []
def on_export(frame, undownloaded_list):
    undownloaded_urls = undownloaded_list.GetItems()
    if not undownloaded_urls:
        wx.MessageBox("没有未下载的网址", "提示", wx.OK|wx.ICON_INFORMATION)
        return
    
    with wx.FileDialog(frame, "保存未下载列表", wildcard="Text files (*.txt)|*.txt",
                     style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return
        
        path = fileDialog.GetPath()
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(undownloaded_urls))
            wx.MessageBox("未下载列表导出成功", "提示", wx.OK|wx.ICON_INFORMATION)
        except Exception as e:
            wx.MessageBox(f"导出失败: {str(e)}", "错误", wx.OK|wx.ICON_ERROR)
def start_download(urls, thread_count, gauge, remaining_label, undownloaded_list, main_site, download_dir, window):
    global stop_download
    stop_download = False
    
    if not urls:
        wx.MessageBox("请先导入网址文件", "错误", wx.OK|wx.ICON_ERROR)
        return
    

    if main_site and not main_site.endswith('/'):
        main_site += '/'

  
    wx.CallAfter(undownloaded_list.Set, [])
    
    total = len(urls)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        futures = []
        for current_url in urls:
            if stop_download:  
                break
          
            if main_site and not current_url.startswith('http'):
                current_url = main_site + current_url
            future = executor.submit(download_file, current_url, download_dir)
            futures.append((current_url, future))
        
        while completed < total and not stop_download: 
            for url_future in futures:
                current_url, future = url_future
                if future.done():
                    completed += 1
                    result = future.result()
                    if not result:  
                        wx.CallAfter(undownloaded_list.Append, current_url)
                    wx.CallAfter(gauge.SetValue, int(completed/total*100))
                    wx.CallAfter(remaining_label.SetLabel, f"剩余项: {total - completed}")
                    futures.remove(url_future)
            wx.MilliSleep(100)
    
    if not stop_download:
        wx.MessageBox("下载完成", "提示", wx.OK|wx.ICON_INFORMATION)
    window.Close()
def download_file(url, download_dir):
    try:
        if stop_download:  
            return False
            
      
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        headers = {"user-agent": ua}
        
        response = requests.get(url, stream=True, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"下载失败: {url} 状态码: {response.status_code}")
            return False
            
       
        os.makedirs(download_dir, exist_ok=True)
        
        
        filename = os.path.basename(url)
        if not filename:  
            filename = "download_" + str(int(time.time())) + ".bin"
        local_path = os.path.join(download_dir, filename)
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*8):
                if chunk:
                    if stop_download:
                        f.close()
                        os.remove(local_path)
                        return False
                    f.write(chunk)
        
        print(f"文件保存成功: {local_path}")
        wx.CallAfter(show_download_complete_notification, local_path)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"下载请求失败: {url} 错误: {str(e)}")
        return False
    except IOError as e:
        print(f"文件保存失败: {url} 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"未知错误: {url} 错误: {str(e)}")
        return False
def download_file(url, download_dir):
    try:
        if stop_download:
            return False
            
    
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
        headers = {"user-agent": ua}
        
        response = requests.get(url, stream=True, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"下载失败: {url} 状态码: {response.status_code}")
            return False
            
      
        os.makedirs(download_dir, exist_ok=True)
        
        filename = os.path.basename(url)
        if not filename:  
            filename = "download_" + str(int(time.time())) + ".bin"
        local_path = os.path.join(download_dir, filename)
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024*8):
                if chunk:
                    f.write(chunk)
        
        print(f"文件保存成功: {local_path}")
        wx.CallAfter(show_download_complete_notification, local_path)
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"下载请求失败: {url} 错误: {str(e)}")
        return False
    except IOError as e:
        print(f"文件保存失败: {url} 错误: {str(e)}")
        return False
    except Exception as e:
        print(f"未知错误: {url} 错误: {str(e)}")
        return False

def show_download_complete_notification(local_path):
    toast = Notification(
        app_id="Advanced Network Toolset",
        title="下载完成",
        msg=f"文件已保存到：{local_path}",
        duration="long"
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()

if __name__ == "__main__":
    create_download_app()
