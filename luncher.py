
import os,wx

roaming_path = os.getenv('APPDATA') + ''

target_folder = os.path.join(roaming_path, "NetDownloader")

if not os.path.exists(target_folder):
    os.makedirs(target_folder)
print(target_folder)
try:
    f=open(target_folder+"\dir.txt","w")
    f.write("D:/downloads/")
    f.close()
except Exception as e:
        wx.MessageBox(f"失败: {str(e)}", "错误", wx.OK | wx.ICON_ERROR)
import Window