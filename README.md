# Database
实现一个航班、航线的管理系统，连接数据库，并绑定UI界面


思路分析：

链接数据库提供好的数据库

用event manager实现用来与Views交互的Engine，用来处理各个事件

修改Engine里的main.py，尤其是process_events函数

import sqlite3, 将SQLite部署在内存里，把引号里的内容换成磁盘地址，database里的内容会存在对应位置
