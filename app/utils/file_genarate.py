import uuid
import datetime
import os
import time
from werkzeug.utils import secure_filename


class File(object):
    def __init__(self, file_obj, save_path):
        self.file_obj = file_obj
        self.save_path = save_path

    def safe_filename_save(self):
        '''返回一个加密后的文件名'''
        res = os.path.splitext(secure_filename(self.file_obj.filename))
        name = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S') + uuid.uuid4().hex + res[-1])
        self.__save_file(name)
        return name

    def __save_file(self, filename):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
        self.file_obj.save(os.path.join(self.save_path, filename))

    def exit_filename(self, oldname):
        '''如果更新了文件'''
        if self.file_obj.filename:
            try:
                os.remove(os.path.join(self.save_path, oldname))
            except FileNotFoundError as e:
                pass
            except PermissionError as e:
                os.remove(os.path.join(self.save_path, oldname))
            return self.safe_filename_save()
        else:
            return oldname

    def save_user_logo(self,oldname):
        if not self.file_obj.filename:
            print(self.file_obj.filename)
            return oldname
        else:
            if not os.path.exists(self.save_path):
                os.makedirs(self.save_path)
            savepath = os.path.join(self.save_path, self.file_obj.filename)
            self.file_obj.save(savepath)
            if oldname is not None:
                os.remove(oldname)
            return self.file_obj.filename
