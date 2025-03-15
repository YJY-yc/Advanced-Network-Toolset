import os
import wx
import time

from winotify import Notification
LAST_UPDATE_TIME = time.mktime(time.strptime("2025-3-15", "%Y-%m-%d"))  

roaming_path = os.getenv('APPDATA') + ''
target_folder = os.path.join(roaming_path, "NetDownloader")

if not os.path.exists(target_folder):
    os.makedirs(target_folder)
    toast = Notification(app_id="Advanced Network Toolset",
                        title="初始化完成",
                        msg=f"数据目录已创建：{target_folder}")
    toast.show()
else:
    current_time = time.time()
    if current_time - LAST_UPDATE_TIME > 1814400:
       
        update_toast = Notification(
            app_id="Advanced Network Toolset",
            title="更新提示",
            msg="当前版本已超过3周未更新，存在可能的更新，请检查更新"
        )
        update_toast.add_actions(
            label="检查更新",
            launch="https://github.com/YJY-yc/Advanced-Network-Toolset"
        )
        
        
        update_toast.show()

print(target_folder)
try:
    f=open(target_folder+"\dir.txt","w")
    f.write("D:/downloads/")
    f.close()
except Exception as e:
    wx.MessageBox(f"创建目录失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
import Window
