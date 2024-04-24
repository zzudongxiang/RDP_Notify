#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os, sys, json
import socket, smtplib
from datetime import datetime
from plyer import notification
from email.mime.text import MIMEText


def read_log(log_path):
    try:
        if os.path.exists(log_path):
            with open(log_path, "r+", encoding="utf-8") as file:
                login_history = file.readlines()
            login_history = list(map(str.strip, login_history))
            login_history = [x for x in login_history if len(x) > 0]
            if len(login_history) > 30:
                login_history = login_history[-30:]
                login_history.insert(0, "... ...")
            login_history = "\r\n".join(login_history)
        else:
            login_history = "暂无记录"
    except:
        login_history = "记录读取失败"
    return login_history


def write_log(log_path, mail_recver, host_info, notify_msg):
    try:
        log_msg = [f"[{datetime.now()}] Windows远程登录到{host_info}\r\n"]
        if len(notify_msg) > 0:
            log_msg.append(
                f"[{datetime.now()}] >> 发送登录日志到<{mail_recver}>失败\r\n"
            )
        log_msg.append(f'[{datetime.now()}] {"-" * 40}\r\n')
        with open(log_path, "a+", encoding="utf-8") as file:
            file.writelines(log_msg)
    except:
        notify_msg = (
            f"{notify_msg}\r\n" if len(notify_msg) > 0 else ""
        ) + "⚠文件记录错误!"
    return notify_msg


def send_mail(config, notify_msg):
    try:
        mail_msg = MIMEText(config["mail_content"], "plain", "utf-8")
        mail_msg["Subject"] = config["mail_subject"]
        mail_msg["From"] = config["mail_sender"]
        mail_msg["To"] = config["mail_recver"][0]
        smtp_obj = smtplib.SMTP()
        smtp_obj.connect(config["mail_smtp_domain"], config["mail_smtp_port"])
        smtp_obj.login(config["mail_sender"], config["mail_passwd"])
        smtp_obj.sendmail(
            config["mail_sender"], config["mail_recver"], mail_msg.as_string()
        )
        smtp_obj.quit()
    except:
        notify_msg = (
            f"{notify_msg}\r\n" if len(notify_msg) > 0 else ""
        ) + "⚠邮件发送失败!"
    return config["mail_recver"][0], notify_msg


host_info = f"{socket.gethostname()} ({socket.gethostbyname(socket.gethostname())})"
root_path = os.path.dirname(sys.argv[0])
log_path = f"{root_path}/login.log"
with open(f"{root_path}/config.json", "r+", encoding="utf-8") as file:
    config = json.load(file)
config["mail_content"] = "\r\n".join(config["mail_content"])
config["mail_content"] = config["mail_content"].replace("%now%", str(datetime.now()))
config["mail_content"] = config["mail_content"].replace("%host_info%", host_info)
config["mail_content"] = config["mail_content"].replace(
    "%login_history%", read_log(log_path)
)
mail_recver, notify_msg = send_mail(config, "")
notify_msg = write_log(log_path, mail_recver, host_info, notify_msg)
notification.notify(
    title="Remote Login Notify",
    message=f"当前远程登录行为已记录\r\n{notify_msg}",
    app_icon=f"{root_path}/favicon.ico",
    timeout=5,
)
