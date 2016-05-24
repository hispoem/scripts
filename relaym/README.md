开发初衷：
为了开发和运维排查问题，并能追踪个人操作，故而将通用账号（非root）和个人账号分开；
通用账号用作服务部署，个人账号用于排查问题（个人账号拥有通用账号组的权限）。

实现功能：
个人账号（实名制）实现无密码登录跳板机（脚本部署主机），并从跳板机无密码登录任何授权业务主机，
该个人账号拥有通用用户组权限，可排查和解决线上问题，出问题时可及时通过历史操作记录追踪。

1、脚本安装部署：
(1)部署操作：
直接部署relaym/bin目录即可，其它数据、日志及公钥目录会在执行relays脚本时自动创建。
将relaym目录搁在部署目录（譬如/usr/local/）下，并将bin目录（譬如/usr/local/relaym/bin）加入root环境变量即可，请勿直接做软连接使用（脚本中涉及的相对目录有可能会影响执行结果）。
加入环境变量后不带任何参数执行relays会自动创建相关目录，并授予相关权限（确保脚本及数据只有root有读取及执行权限）。
(2)初始化操作：
将用户公钥上传至pubkey目录；
将host.list上传至data目录。

2、脚本目录简介：
bin目录包含三个可执行脚本：relays  remote_ca.exp  remote_da.exp；
relays: relay主机（跳板机）和远程业务主机账号创建及删除主脚本；
remote_ca.exp: 远程创建账号及赋权脚本（expect实现）；
remote_da.exp: 远程删除账号脚本（expect实现）。

pubkey目录是用户公钥上传目录，将要开通账号的员工的公钥上传到此目录即可；
公钥命名方式为“账号名＋.pub”（譬如hispoem.pub）。

logs目录纪录创建及删除的详细操作（caccount.log：创建账号日志，daccount.log：删除账号日志）。

data目录会包含两个文本文件：account.list  host.list；
account.list: 执行创建账号动作后会自动生成，记录形式为“用户名 主机名”，按用户名排序。删除账号会同步更新该文本；
host.list: 要开通账号的主机信息列表，需要管理员更新和维护（内容为expect脚本需要的信息），出于安全考虑执行脚本后会不可读。
示例内容如下（格式为：主机名 主机IP 通用用户密码 root密码）：
ops-01 192.168.168.11 userpwd rootpwd
ops-02 192.168.168.12 userpwd rootpwd

3、使用示例：
直接执行relays -h获取简单帮助；
#relays -h
***************Command options***************
-c: create account
-d: delete account
-s: the account of the machine
-a: the account of all machine
****************Usage example****************
/usr/local/relaym/bin/relays -c user1:host1
/usr/local/relaym/bin/relays -c user1,user2,user3:host1,host2,host3
/usr/local/relaym/bin/relays -d -a user1
/usr/local/relaym/bin/relays -d -s user1:host1

创建用户是批量操作，删除用户是单个操作；
relays -c hispoem:ops-01 #在主机ops-01上建账号hispoem
relays -c hispoem1,hispoem2:ops-01,ops-02 #在主机ops-01,ops-02上创建账号hispoem1和hispoem2
relays -d -a hispoem  #删除所有主机hispoem帐号
relays -d -s hispoem:ops-01 #删除主机ops-01的hispoem帐号
