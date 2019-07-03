from JenkinsConnector import jenkins_connector
from in_memory_storage_provider import StorageProvider
import json

automation_jenkins = jenkins_connector(
    'http://jenkinsserver2:8080', 'prsubrama', 'XXXX')
scm_jenkins = jenkins_connector('http://10.35.242.150', 'prsubrama', 'XXXX')


def get_job_details(job_name):
    conn = automation_jenkins.get_connection()
    data = conn.get_job_info(job_name, 10)
    return data


def get_build_details(job_name, build_number):
    conn = automation_jenkins.get_connection()
    data = conn.get_build_info(job_name, build_number)
    return data


def get_incoming_items(incoming, outgoing):
    returnable_incoming = []
    build_map_store = StorageProvider(incoming+'.json')
    scm_jobs = scm_jenkins.get_connection().get_job_info(incoming)
    builds = scm_jobs['builds']
    for i in range(0, 10):
        RAM = build_map_store.read_data()
        if(str(builds[i].get('number')) in RAM.keys()):
            print('.')
        else:
            print('-')
            build_info = scm_jenkins.get_connection().get_build_info(
                incoming, builds[i].get('number'))
            build_map_store.append_data(
                build_info['id'], build_info['displayName'])
            build_map_store.persist_data()
    RAM = build_map_store.read_data()
    for items in RAM.values():
        returnable_incoming.append(items)
    return returnable_incoming


def get_outgoing_items(outgoing):
    returnable_outgoing = []
    auto_build_map_store = StorageProvider(outgoing+'.json')
    automation_jobs = automation_jenkins.get_connection().get_job_info(outgoing)
    automation_builds = automation_jobs['builds']
    for i in range(0, 40):
        A_RAM = auto_build_map_store.read_data()
        if(str(automation_builds[i].get('number')) in A_RAM.keys()):
            print('.')
        else:
            print('-')
            build_info = automation_jenkins.get_connection().get_build_env_vars(
                outgoing, automation_builds[i].get('number'))
            if('BuildVersion' in build_info['envMap'].keys()):
                auto_build_map_store.append_data(automation_builds[i].get('number'), build_info['envMap']['BuildVersion'])
                auto_build_map_store.persist_data()
    A_RAM = auto_build_map_store.read_data()
    for items in A_RAM.values():
        returnable_outgoing.append(items)
    return returnable_outgoing


if __name__ == "__main__":

    MASTER_DATA = {}
    run_conifg = json.load(open('run_config.json'))
    # BUILD INCOMING
    for contents in run_conifg:
        incoming = contents['incoming']
        outgoing = contents['outgoing']
        MASTER_DATA[incoming] = {}
        MASTER_DATA[incoming]['incoming'] = get_incoming_items(incoming, outgoing)
        MASTER_DATA[outgoing] = {}
        MASTER_DATA[outgoing]['outgoing'] = get_outgoing_items(outgoing)

    print(MASTER_DATA)

    json.dump(MASTER_DATA, open('output.txt', 'w+'))
