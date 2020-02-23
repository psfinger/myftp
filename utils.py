import configparser


def getconfig(opt):
    # 获取config.ini配置文件的信息
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config.get('ftpd', opt)
