import json
import time
import io
from os import path


class StorageProvider():
    def __init__(self, filename):
        self.data_block = filename
        self.data = {}
        if(not path.exists(filename)):
            json.dump(self.data, open(self.data_block, 'w+'))
        


    def read_data(self):
        if(self.data == {}):
            return json.load(open(self.data_block))
        else:
            return self.data

    def write_data(self, data):
        try:
            self.data = data
            return True
        except:
            return False

    def persist_data(self):
        try:
            json.dump(self.data, open(self.data_block, 'w+'))
            return True
        except:
            return False

    def append_data(self, key, value):
        try:
            evals = 'self.data'
            for items in str(key).split('.'):
                evals = evals+'["'+items+'"]'            
            try:
                exec(str(value))
                evals = evals+' = '+str(value)
            except:
                evals = evals+' = "'+str(value)+'"'
            exec(evals)
            return True
        except:
            print('fail')
            return False

    def __del__(self):
        #writer(self.data_block,self.data)
        pass
       