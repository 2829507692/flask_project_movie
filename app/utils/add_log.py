from flask import session,request
from app import models ,mysql_db
class AddLog():
    @staticmethod
    def add_admin_log():
        log=models.AdminLog(
            admin_id=session['id'],
            ip=request.remote_addr
        )
        mysql_db.session.add(log)
        mysql_db.session.commit()

    @staticmethod
    def add_user_log():
        log=models.UserLog(
            user_id=session['id'],
            ip=request.remote_addr
        )
        mysql_db.session.add(log)
        mysql_db.session.commit()

    @classmethod
    def add_oplog(cls,reason):
        OP=models.OpLog(
            ip=request.remote_addr,
            admin_id=session['id'],
            reason=reason
        )
        mysql_db.session.add(OP)
        mysql_db.session.commit()



if __name__ == '__main__':
    AddLog.add_oplog()