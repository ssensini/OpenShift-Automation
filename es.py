import subprocess
import sys

commands, indexes = [], []

print("##############################################")
print("Welcome to Elasticsearch cleaning automation. "
      "Please, before proceeding, login to the cluster "
      "as admin using 'oc login'.")
print("##############################################")

logged_in = "oc whoami"
check_logged_in_cmd = process = subprocess.Popen(logged_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
stdout, stderr = process.communicate()
if "error" in stdout.decode('utf-8').lower() or "error" in stderr.decode('utf-8').lower():
    print("You're not logged in. Please, login as 'admin' before continue.")
    sys.exit()

pod_name = input('Insert the Elasticsearch pod name (you\' find it in \'openshift-logging\' namespace): ')

if pod_name:
    get_indexes_cmd = 'oc exec ' + pod_name + ' --container elasticsearch -- es_util --query=_cat/indices?h=index -n openshift-logging'
    print(get_indexes_cmd)
    process = subprocess.Popen(get_indexes_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    print('Processing...')

    stdout, stderr = process.communicate()
    if stderr:
        with open('tot_indexes.txt', 'w') as file:
            file.write(stdout.decode('utf-8'))
    else:
        print(stderr.decode('utf-8'))
        sys.exit()

    to_delete = input('Insert a pattern you\'d like to match OR a date to delete -use format YYYY.MM.DD, partial date is admitted-: ')

    with open('tot_indexes.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if to_delete in line:
                line = line.replace('\n', '')
                indexes.append(line)
                command = 'oc exec ' + pod_name + '  --container elasticsearch -- es_util --query=' + line + ' -X DELETE -n openshift-logging'
                commands.append(command)
else:
    print("Elasticsearch pod name seems wrong. Try again.")

if len(indexes) != 0:
    print("#######################")
    print("FOUND INDEXES:")
    print("#######################")
    for index in indexes:
        print(index)
    print("#######################")

    confirm = input('The following indexes will be deleted: confirm? Y/n: ')
    if confirm.lower() == 'y':
        print("--------------------------------")
        for command, index in zip(commands, indexes):
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process.communicate()
            # print("Command:", command)
            print("Current index:", index)
            print("Status:", stdout.decode('utf-8'))
            print("--------------------------------")
        print("Done.")
else:
    print("No indexes found with the date inserted.")
