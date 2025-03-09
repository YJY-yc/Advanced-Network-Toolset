import tkinter
import requests
from tkinter import messagebox,ttk

def download_file(url, local_path):
    global dirs
    # 发送GET请求
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"
    headers = {"user-agent": ua}
    try:
        response = requests.get(url, stream=True,headers=headers)
    except Exception as e:
        tkinter.messagebox.showwarning(title="",message="获取链接码失败:\n"+str(e)+"\n请检查网络、链接是否正确")
  
    
    # 检查请求是否成功
    if response.status_code == 200:
        # 打开本地文件，准备写入
        root=tkinter.Tk()
        root.geometry("500x300")
        root.title("下载...")
        content_size=0xffffff
        try:
            content_size = int(response.headers['content-length']) #下载文件总大小
        except:
            print("文件大小未知")
        all_size=int(content_size/(1024*8))
        Progressbar0=tkinter.ttk.Progressbar(root,length=600,orient="horizontal",mode="determinate")
        Progressbar0.pack()
        title=tkinter.Label(root,text="正在下载"+local_path+"  关闭此窗口以结束任务")
        title.pack()
        Progressbar0["maximum"]=all_size
        Progressbar0["value"]=0
        root.update_idletasks()
        wr=0
        try:
            with open(local_path, 'wb') as f:
            
                for chunk in response.iter_content(chunk_size=1024*8):
                    if chunk:
                        wr+=1
                        Progressbar0["value"]+=1
                        
                        root.update_idletasks()
                        root.update()
                        f.write(chunk)
                        
            print("文件下载成功，保存在：", local_path)
            
            root.destroy()
            return 0
        except Exception as e:
            tkinter.messagebox.showwarning(title="",message="保存文件失败:\n"+str(e)+"\n请检查保存位置是否已满或有无权限")
    else:
        print("文件下载失败，状态码：", response.status_code)
        tkinter.messagebox.showerror(title="",message="错误:"+ str(response.status_code)+"请不要关闭下载界面")
    
    root.mainloop()
if __name__ == '__main__':
    download_file("https://cdn.modrinth.com/data/o1tyE5vJ/versions/dmEZkFA7/custom-crosshair-mod-v1.5.2-forge-mc1.19.3.jar","test.png")