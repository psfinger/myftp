# -*- coding:utf-8 -*-
import multiprocessing

import wx
import os
import sys
import configparser

import ftpserver
from utils import getconfig
import time
import threading
import socket


class FTPFrame(wx.Frame):
    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)

        # 创建panel
        panel = wx.Panel(self)
        font = wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL)
        # 创建复选框，并绑定事件
        self.check = wx.CheckBox(panel, -1, '使用账户密码登录', pos=(20, 20), size=(200, -1))
        self.check.SetFont(font)
        self.Bind(wx.EVT_CHECKBOX, self.onchecked)


        # 创建静态文本和文本输入框
        self.userlabel = wx.StaticText(panel, label="用户名:", pos=(35, 45))
        self.userlabel.SetFont(font)
        self.usertext = wx.TextCtrl(panel, -1, '', size=(95, 20), pos=(90, 42), style=wx.TE_READONLY)
        self.passlabel = wx.StaticText(panel, label="密码:", pos=(195, 45))
        self.passlabel.SetFont(font)
        self.passtext = wx.TextCtrl(panel, -1, '', size=(95, 20), pos=(235, 42), style=wx.TE_PASSWORD)
        self.passtext.SetEditable(False)
        self.dirlabel = wx.StaticText(panel, label="FTP目录:", pos=(23, 72))
        self.dirlabel.SetFont(font)
        self.dirtext = wx.TextCtrl(panel, -1, os.getcwd(), size=(215, 20), pos=(88, 70), style=wx.TE_READONLY)

        # 绑定退出事件
        self.Bind(wx.EVT_CLOSE, self.onclose)



        # 创建按钮，并且绑定按钮事件
        self.button = wx.Button(panel, -1, '更改', pos=(310, 70), size=(40, 20))
        self.button.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.Bind(wx.EVT_BUTTON, self.onclick, self.button)

        self.portlabel = wx.StaticText(panel, label="FTP端口:", pos=(23, 104))
        self.portlabel.SetFont(font)
        self.porttext = wx.TextCtrl(panel, -1, '21', size=(51, 20), pos=(88, 102))
        self.startbutton = wx.Button(panel, -1, '启动FTP', pos=(160, 130), size=(70, 30))
        self.startbutton.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
        self.Bind(wx.EVT_BUTTON, self.startftp, self.startbutton)

        # 加载配置文件，使程序恢复到退出前的界面
        if os.path.isfile('config.ini'):
            if getconfig('anonymous') == 'False':
                self.check.SetValue(1)
                self.usertext.SetEditable(1)
                self.passtext.SetEditable(1)
            self.usertext.SetValue(getconfig('user'))
            self.passtext.SetValue(getconfig('password'))
            self.porttext.SetValue(getconfig('port'))
            self.dirtext.SetValue(getconfig('dir'))
        self.urllabel = wx.StaticText(panel, label="", pos=(80, 170))
        self.urllabel.SetFont(font)

    def onclick(self, event):  # 选择FTP目录
        dlg = wx.DirDialog(self, '选择共享目录')
        if dlg.ShowModal() == wx.ID_OK:
            self.dirtext.SetValue(dlg.GetPath())

    def onclose(self, event):  # 退出事件
        if self.startbutton.GetLabel() == '关闭FTP':
            dlg1 = wx.MessageDialog(None, "FTP正在运行，确认退出吗？", "退出", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dlg1.ShowModal() == wx.ID_YES:
                sys.exit()
        else:
            sys.exit()

    def startftp(self, event):  # 点击 启动FTP 按钮事件
        if self.startbutton.GetLabel() == '启动FTP':
            self.startbutton.SetLabel('关闭FTP')
            # 把FTP启动信息写入config.ini配置文件中
            config = configparser.ConfigParser()
            config.add_section('ftpd')
            config.set('ftpd', 'anonymous', str(not self.check.GetValue()))
            config.set('ftpd', 'user', self.usertext.GetValue())
            config.set('ftpd', 'password', self.passtext.GetValue())
            config.set('ftpd', 'port', self.porttext.GetValue())
            config.set('ftpd', 'dir', self.dirtext.GetValue())
            with open('config.ini', 'w') as conf:
                config.write(conf)
            time.sleep(1)
            # 创建线程启动FTP
            t = threading.Thread(target=ftpserver.start_ftp)
            t.setDaemon(True)
            t.start()
            iplist = socket.gethostbyname_ex(socket.gethostname())[2]
            ftpurl = ''
            if iplist:
                for ip in iplist:
                    ftpurl += 'FTP地址:ftp://' + ip + ':' + self.porttext.GetValue() + '\n'
            self.urllabel.SetLabel(ftpurl)
        else:
            dlg1 = wx.MessageDialog(None, "FTP正在运行，确认退出吗？", "退出", wx.YES_NO | wx.ICON_EXCLAMATION)
            if dlg1.ShowModal() == wx.ID_YES:
                sys.exit()

    def onchecked(self, event):  # 复选框事件
        self.usertext.SetEditable(event.IsChecked())
        self.passtext.SetEditable(event.IsChecked())


if __name__ == '__main__':
    app = wx.App()  # 实例化wx.App
    # 创建顶级窗口，并且窗口不可改变尺寸
    window = FTPFrame(None, title="FTP服务器", size=(390, 260), pos=(400, 300),
                      style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
    window.Show(True)  # 窗口可见
    app.MainLoop()  # 主循环，处理事件
