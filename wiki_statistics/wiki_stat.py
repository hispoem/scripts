#!/usr/bin/env python
#encoding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime
import smtplib
import traceback
from email.mime.text import MIMEText
from email.header import Header
import MySQLdb

class WikiCount(object):
    '''wiki产出统计'''
    date = datetime.datetime.now().date() - datetime.timedelta(days=1)
    conf = {
        'host': 'smtp.xxx.com',
        'port': 465,
        'sender': 'sender@xxx.com',
        'password': '123456',
        'receiver': 'hispoem@xxx.com'
    }

    def db_conn(self):
        '''建立数据库连接'''
        conn = MySQLdb.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='123456',
            db='confluence',
            charset='utf8'
        )
        cursor = conn.cursor()
        return conn, cursor

    def get_all_id_name_dict(self):
        '''获取所有id:中文名字字典'''
        all_id_name_dict = dict()
        sql_all_id_name = "select user_key,display_name from user_mapping left join cwd_user on user_mapping.`username`=cwd_user.`lower_user_name`"
        cursor = self.db_conn()[1]
        cursor.execute(sql_all_id_name)
        all_id_name_result = cursor.fetchall()
        for id_name in all_id_name_result:
            all_id_name_dict[id_name[0]] = id_name[1]
        return all_id_name_dict

    def get_mid_mcount_dict(self):
        '''获取有修改操作的字典,id:修改个数'''
        mid_mcount_dict = dict()
        sql_mid_mcount = "select LASTMODIFIER,count(1) from confluence.CONTENT where left(LASTMODDATE,10)='{0}' group by LASTMODIFIER".format(self.date)
        cursor = self.db_conn()[1]
        cursor.execute(sql_mid_mcount)
        mid_mcount_result = cursor.fetchall()
        for mid_mcount in mid_mcount_result:
            if mid_mcount[0] == None:
                continue
            else:
                mid_mcount_dict[mid_mcount[0]] = mid_mcount[1]
        return mid_mcount_dict

    def get_cid_ccount_dict(self):
        '''获取有创建操作的字典,id:创建个数'''
        cid_ccount_dict = dict()
        sql_cid_ccount = "select CREATOR,COUNT(1) from (select DISTINCT TITLE,CREATOR from confluence.CONTENT where left(CREATIONDATE,10)='{0}')temp GROUP BY CREATOR".format(self.date)
        cursor = self.db_conn()[1]
        cursor.execute(sql_cid_ccount)
        cid_ccount_result = cursor.fetchall()
        for cid_ccount in cid_ccount_result:
            if cid_ccount[0] == None:
                continue
            else:
                cid_ccount_dict[cid_ccount[0]] = cid_ccount[1]
        return cid_ccount_dict

    def run(self):
        '''入口函数'''
        # 所有数据字典(id:[新增数,修改数])
        id_all_dict = dict()
        conn = self.db_conn()[0]
        all_id_name_dict = self.get_all_id_name_dict()
        mid_mcount_dict = self.get_mid_mcount_dict()
        cid_ccount_dict = self.get_cid_ccount_dict()
        mid_list = mid_mcount_dict.keys()
        cid_list = cid_ccount_dict.keys()
        id_all_list = list(set(mid_list + cid_list))
        # print "今日wiki共编辑", id_all_list.__len__(), "人次,详情如下:\n"
        # print "\n姓名\t\t新增wiki数\t\t修改wiki数"
        content = ["<th>编辑用户</th><th>新增wiki数</th><th>修改wiki数</th>"]
        for id in id_all_list:
            if not cid_ccount_dict.has_key(id):
                cid_ccount_dict[id] = 0
            if not mid_mcount_dict.has_key(id):
                mid_mcount_dict[id] = 0
            id_all_dict[id] = [cid_ccount_dict[id], mid_mcount_dict[id]]
            # print all_id_name_dict[id], '\t\t', id_all_dict[id][0], '\t\t\t\t', id_all_dict[id][1]
            content = content + [unicode("<td>{0}</td><td>{1}</td><td>{2}</td>", "utf-8").format(all_id_name_dict[id], id_all_dict[id][0], id_all_dict[id][1])]
        constr = "<p><b>昨日wiki共编辑 {0} 人次,详情如下:</b></p>".format(id_all_list.__len__()) + '<table><tr>' + '</tr><tr>'.join(content) + '</tr></table>'
        constr = str(constr)

        msg = MIMEText(constr,'html','utf-8')
        msg["Accept-Language"] = "zh-CN"
        msg["Accept-Charset"] = "ISO-8859-1,utf-8"
        msg['subject'] = Header('[统计]昨日wiki统计{0}'.format(self.date),'utf-8')
        msg['from'] = self.conf['sender']
        msg['to'] = self.conf['receiver']

        try:
            smtp = smtplib.SMTP_SSL(self.conf['host'], self.conf['port'])
            smtp.set_debuglevel(1)
            smtp.login(self.conf['sender'], self.conf['password'])
            smtp.sendmail(self.conf['sender'], self.conf['receiver'], msg.as_string())
            smtp.quit()
        except Exception, e:
            traceback.print_exc()
            print str(e)

        conn.close()


if __name__ == "__main__":
    wikicount = WikiCount()
    wikicount.run()
