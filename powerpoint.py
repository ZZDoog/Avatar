# ppt转视频算法

import win32com.client
import time
import os
import pythoncom

def cov_ppt(src, dst):

    pythoncom.CoInitialize()
    PowerPoint = win32com.client.Dispatch('PowerPoint.Application')
    target = PowerPoint.Presentations.Open(src, WithWindow=False)
    target.CreateVideo(dst, VertResolution=720)
    while True:
        time.sleep(1)
        try:
            os.rename(dst, dst)
            break
        except Exception:
            pass
    PowerPoint.Quit()
    return

