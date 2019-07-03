import jenkins

class jenkins_connector:
    def __init__(self,url , user , password):
        self.server = jenkins.Jenkins(url, user, password)
    def get_connection(self):
        return self.server