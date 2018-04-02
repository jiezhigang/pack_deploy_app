# -*- coding: utf-8 -*-
import time
import logging
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import render
from kernel_program.Linux import Linux

logger = logging.getLogger('django.request')


# Create your views here.


# 进入打包首页，创建socket连接
def pack_index(request):
    # 视图与数据分离
    context = {}
    context['rlt'] = ''
    return render(request, 'pack.html', context)


# 接收POST请求数据
def pack_post(request):
    request.encoding = 'utf-8'
    ctx = {}
    if request.META.has_key('HTTP_X_FORWARDED_FOR'):
        ip = request.META['HTTP_X_FORWARDED_FOR']
    else:
        ip = request.META['REMOTE_ADDR']
    if request.POST:
        # 配置选项
        host = request.POST['ip'].encode('unicode-escape').decode('string_escape')  # '192.168.58.142'  # Telnet服务器IP
        username = 'adm'  # 登录用户名
        # password = 'venus70'  # 登录密码
        password = request.POST['password'].encode('unicode-escape').decode('string_escape')
        finish = '# '  # 命令提示符
        commands = ['show config']
        try:
            build_flag = request.POST['build_flag']
            build = ''
            if build_flag != '':
                build = build_flag.encode('unicode-escape').decode('string_escape')
            if build == 'on':
                print('开始打包')
                logger.info(ip + "执行打包操作")
                # 启用打包工具
                linux_host = Linux('192.168.58.69', 'root', 'venus60')
                linux_host.connect()
                linux_host.send('cd /home/wlc/code/Linux_IDS/build_31/', r' build_31]#')
                linux_host.send('./build31.sh', r'build_31]#')
                linux_host.close()
        except Exception:
            print('不进行打包')
        request.encoding = 'utf-8'
        # 开始灌装
        logger.info(ip + "对" + host + "开始灌装")
        try:
            s = do_telnet(host, username, password, finish, commands, request)
            ctx['rlt'] = s
            logger.info(ip + "对" + host + "完成灌装")
        except Exception:
            logger.error("灌装失败，与引擎" + host + "连接失败")
            return HttpResponse("灌装失败，与引擎" + host + "连接失败")
        return HttpResponse('灌装完成')
    return render(request, "pack.html", ctx)


def do_telnet(host, username, password, finish, commands, request):
    import telnetlib
    '''''Telnet远程登录：Windows客户端连接Linux服务器'''

    # 连接Telnet服务器
    tn = telnetlib.Telnet(host, port=23, timeout=100)
    tn.set_debuglevel(2)

    # 输入登录用户名
    tn.read_until('Username: ')
    tn.write(username + '\n')

    # 输入登录密码
    tn.read_until('Password: ')
    tn.write(password + '\n')

    # 输入登录密码
    tn.read_until('> ')
    tn.write('en' + '\n')
    # 登录完毕后执行命令
    tn.read_until(finish)
    for command in commands:
        tn.write('%s\n' % command)
        print('-------------------------output----------------------------')
        # 执行完毕后，终止Telnet连接（或输入exit退出）
    s = ''  # tn.read_until(finish)
    # 登录后台
    tn.write('dia' + '\n')
    # 输入登录密码
    tn.read_until('Password: ')
    tn.write('hwlypaqdtk!' + '\n')
    finish = '[/]#'
    tn.read_until(finish)
    #    tn.write('df' + '\n')
    #    s1 = s + tn.read_until(finish)
    #    tn.read_until(finish)
    tn.write('cd /hdisk/' + '\n')
    time.sleep(1)
    # 清理数据
    finish = '[/hdisk]# '
    tn.read_until(finish)
    try:
        delete_db_flag = request.POST['delete_flag']
        delete_flag = ''
        if delete_db_flag != '':
            delete_flag = delete_db_flag.encode('unicode-escape').decode('string_escape')
        if delete_flag == 'on':
            print('清除数据')
            tn.write('rm -fr mysql_data/ mongodb_data/' + '\n')
            tn.read_until(finish)
    except Exception:
        print('保留数据库')
    # 清除程序代码
    tn.write('rm -fr ids_web/' + '\n')
    tn.read_until(finish)
    tn.write('./ftp' + '\n')
    time.sleep(1)
    return_string = tn.read_very_eager()
    if 'ftp>' in return_string:
        print ('可以使用ftp')
        tn.write('open 192.168.57.223' + '\n')
        tn.read_until('Name (192.168.57.223:root): ')
        tn.write('ids' + '\n')
        tn.read_until('Password:')
        tn.write('venus70' + '\n')
        tn.read_until('ftp> ')
        tn.write('cd /linux_31_temp' + '\n')
        tn.read_until('ftp> ')
        tn.write('get ids.tar.gz' + '\n')
        tn.read_until('ftp> ')
        print('下载成功……')
        s1 = s + '\r\ndownload success\r\n'
        tn.write('quit' + '\n')
        tn.read_until(finish)
    else:
        return '请下载FTP工具'
    print ('~~~~~~~~~')
    try:
        tn.write('reboot' + '\n')
        s2 = s1 + 'reboot'
        tn.read_until(finish)
        tn.close()  # tn.write('exit\n')
    except Exception:
        s2 = s2 + 'close connection'
    return s2
