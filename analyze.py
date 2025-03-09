import wx,requests
from bs4 import BeautifulSoup


# 分析网页的函数
def analyze_webpage(url):

    try:
        response = requests.get(url, verify=False)  
        
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取网页标题
        title = soup.title.string if soup.title else "无标题"
        
        # 提取所有链接
        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        # 提取所有图片
        images = [img['src'] for img in soup.find_all('img', src=True)]
        
        # 提取正文文本
        text = soup.get_text()
        
        return {
            'title': title,
            'links': links,
            'images': images,
            'text': text,
            'source': response.text 
        }
    except Exception as e:
        return {'error': str(e)}

def on_analyze_button(url_l):
    
    print(url_l)

    result = analyze_webpage(url_l)
    
    if 'error' in result:
        wx.MessageBox(f"分析失败: {result['error']}", "错误", wx.OK | wx.ICON_ERROR)
        return
    
    # 创建新窗口显示结果
    result_window = wx.Frame(None, title="网页分析结果", size=(600, 400))
    notebook = wx.Notebook(result_window)
    
    # 创建不同的面板
    info_panel = wx.Panel(notebook)
    links_panel = wx.Panel(notebook)
    images_panel = wx.Panel(notebook)
    text_panel = wx.Panel(notebook)
    source_panel = wx.Panel(notebook)
    # 基本信息面板
    info_text = wx.TextCtrl(info_panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(600, 300))
    info_text.SetValue(f"网页标题: {result['title']}\n\n"
                      f"链接数量: {len(result['links'])}\n"
                      f"图片数量: {len(result['images'])}")
    
    # 链接面板
    links_text = wx.TextCtrl(links_panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(600, 300))
    links_text.SetValue("\n".join(result['links']))
    
    # 图片面板
    images_text = wx.TextCtrl(images_panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(600, 300))
    images_text.SetValue("\n".join(result['images']))
    
    # 文本面板
    text_text = wx.TextCtrl(text_panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(600, 300))
    text_text.SetValue(result['text'])

        # 源码面板
    source_text = wx.TextCtrl(source_panel, style=wx.TE_MULTILINE|wx.TE_READONLY, size=(600, 300))
    source_text.SetValue(result['source'])
    
    # 添加面板到笔记本
    notebook.AddPage(info_panel, "基本信息")
    notebook.AddPage(links_panel, "链接")
    notebook.AddPage(images_panel, "图片")
    notebook.AddPage(text_panel, "文本")
    notebook.AddPage(source_panel, "源码")
    
    # 显示窗口
    result_window.Show()
