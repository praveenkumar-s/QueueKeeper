from JenkinsConnector import jenkins_connector
from in_memory_storage_provider import StorageProvider
import json

automation_jenkins = jenkins_connector('http://jenkinsserver2:8080','prsubrama','XXXX')
scm_jenkins = jenkins_connector('http://10.35.242.150','prsubrama','XXXX')


def get_job_details(job_name):
    conn=automation_jenkins.get_connection()
    data = conn.get_job_info(job_name,10)
    return data

def get_build_details(job_name, build_number):
    conn=automation_jenkins.get_connection()
    data = conn.get_build_info(job_name,build_number)
    return data

def build_map(job_name, builds):
    for build in builds:
        if(not build in build_map_store.read_data()):
            value = get_build_details(job_name, build)
            build_map_store.append_data(job_name[build], value)


if __name__ == "__main__":
    MASTER_DATA={}
    run_conifg = json.load(open('run_config.json'))
    #BUILD INCOMING
    for contents in run_conifg:
        build_map_store = StorageProvider(contents['incoming']+'.json')
        scm_jobs= scm_jenkins.get_connection().get_job_info(contents['incoming'])
        builds = scm_jobs['builds']
        for i in range(0,10):
            RAM=build_map_store.read_data()
            if(str(builds[i].get('number')) in RAM.keys()):
                print('.')
            else:
                print('-')
                build_info = scm_jenkins.get_connection().get_build_info(contents['incoming'],builds[i].get('number'))
                build_map_store.append_data(build_info['id'],build_info['displayName'])
                build_map_store.persist_data()
        RAM= build_map_store.read_data()
        MASTER_DATA[contents['incoming']]={}
        MASTER_DATA[contents['incoming']]["incoming"]=[]
        MASTER_DATA[contents['incoming']]["outgoing"]=[]
        for items in RAM.values():
            MASTER_DATA[contents['incoming']]["incoming"].append(items)
        
        #BUILD OUTGOING
        auto_build_map_store = StorageProvider(contents['outgoing']+'.json')
        automation_jobs = automation_jenkins.get_connection().get_job_info(contents['outgoing'])
        automation_builds = automation_jobs['builds']
        for i in range(0,40):
            A_RAM=auto_build_map_store.read_data()
            if(str(automation_builds[i].get('number')) in A_RAM.keys()):
                print('.')
            else:
                print('-')
                build_info = automation_jenkins.get_connection().get_build_env_vars(contents['outgoing'],automation_builds[i].get('number'))
                if('BuildVersion' in build_info['envMap'].keys()):
                    auto_build_map_store.append_data(automation_builds[i].get('number'),build_info['envMap']['BuildVersion'])
                    auto_build_map_store.persist_data()
        A_RAM=auto_build_map_store.read_data()
        for items in A_RAM.values():
            MASTER_DATA[contents['incoming']]["outgoing"].append(items)       
    print(MASTER_DATA)

    json.dump(MASTER_DATA,open('output.txt','w+'))