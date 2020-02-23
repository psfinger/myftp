# coding:utf-8
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import logging
from utils import getconfig
import os


class FTPD:
    def __init__(self):
        authorizer = DummyAuthorizer()
        if getconfig('anonymous') == 'True':
            # 添加匿名用户
            authorizer.add_anonymous(getconfig('dir'), perm='elradfmwM')
        else:
            # 添加用户，需要账号和密码登录
            authorizer.add_user(getconfig('user'), getconfig('password'), getconfig('dir'), perm='elradfmwM')
        handler = FTPHandler  # 初始化处理客户端命令的类
        handler.authorizer = authorizer  # 选择登录方式(是否匿名)
        # logging.basicConfig(filename='ftpd.log', level=logging.INFO)  # 日志信息写入ftpd.log
        address = ('0.0.0.0', getconfig('port'))  # 设置服务器的监听地址和端口
        self.server = FTPServer(address, handler)
        self.server.max_cons = 256  # 给链接设置限制
        self.server.max_cons_per_ip = 5

    def start(self):
        self.server.serve_forever()


def start_ftp():
    ftpd = FTPD()
    ftpd.start()


if __name__ == '__main__':
    start_ftp()
