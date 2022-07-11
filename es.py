import subprocess
import sys
import re

commands, indexes = [], []


def get_pattern(pod_name):
    to_delete = input(
        'Insert a pattern you\'d like to match -OR a date to delete -use format YYYY.MM.DD or YYYY-MM-DD, partial date is admitted-: ')

    with open('tot_indexes.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            splitted = line.split()
            index = splitted[0]
            date = splitted[1]
            size = splitted[2]
            row = index + date + size
            if to_delete in row:
                index = index.replace('\n', '')
                indexes.append({
                    "index": index,
                    "date": date,
                    "size": size
                })
                command = 'oc exec ' + pod_name + '  --container elasticsearch -- es_util --query=' + index + ' -X DELETE -n openshift-logging'
                commands.append(command)


def get_indexes():
    message = "Y"

    while message == "Y":
        try:
            logged_in = "oc whoami"
            process_logged = subprocess.Popen(logged_in, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process_logged.communicate()
            if "error" in stdout.decode('utf-8').lower() or "error" in stderr.decode('utf-8').lower():
                print("You're not logged in. Please, login as 'admin' before continue.")
                sys.exit()
            else:
                print("Great, you're logged as cluster-admin.")

            set_project = "oc project openshift-logging"
            process_project = subprocess.Popen(set_project, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process_project.communicate()
            if "error" in stdout.decode('utf-8').lower() or "error" in stderr.decode('utf-8').lower():
                print("Probably you're not cluster-admin. Please, login as 'admin' before continue.")
                sys.exit()
            else:
                print("Excellent, you're in the right project.")

            print("Getting the Elasticsearch pod name...")

            get_pods = "oc get pods"
            process_get_pods = subprocess.Popen(get_pods, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process_get_pods.communicate()

            pod_name = ""

            if "logging-es" in stdout.decode('utf-8'):
                regex = re.search("logging-es-data-master-[a-zA-Z0-9]{8}-[0-9]-[a-zA-Z0-9]{5}", stdout.decode('utf-8'))
                pod_name = regex.group()

            if len(pod_name) == 0:
                regex = re.search("elasticsearch-[a-zA-Z0-9]{3}-[a-zA-Z0-9]*-[0-9]*-[a-zA-Z0-9]*-[a-zA-Z0-9]*",
                                  stdout.decode('utf-8'))
                pod_name = regex.group()

            if pod_name:
                print("Done.")
                get_indexes_cmd = 'oc exec ' + pod_name + ' --container elasticsearch -- es_util --query=_cat/indices?h=index,creation.date.string,store.size'
                print(get_indexes_cmd)
                process = subprocess.Popen(get_indexes_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                print('Processing...')

                stdout, stderr = process.communicate()
                if len(stderr) == 0:
                    with open('tot_indexes.txt', 'w') as file:
                        file.write(stdout.decode('utf-8'))
                else:
                    print(stderr.decode('utf-8'))
                    sys.exit()
            else:
                print("Pod not found. Maybe it's not active... Try again later!")
                sys.exit()

            get_pattern(pod_name)

            if len(indexes) != 0:
                print("#######################")
                print("FOUND INDEXES:")
                print("#######################")
                for index in indexes:
                    print("INDEX NAME")
                    print(index['index'])
                    print("DATE")
                    print(index['date'])
                    print("SIZE")
                    print(index['size'])
                    print("---------------------------------------------------------------------------------------")
                print("#######################")

                confirm = input('The following indexes will be deleted: confirm? Y/n: ')
                if confirm.lower() == 'y':
                    print("--------------------------------")
                    for command, index in zip(commands, indexes):
                        print(command)
                        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                        stdout, stderr = process.communicate()
                        print("Current index:", index['index'])
                        print("Status:", stdout.decode('utf-8'))
                        print("--------------------------------")
                    print("Done.")
            else:
                print("No indexes found with the date inserted.")

        except KeyboardInterrupt as e:
            print("--------------------------------")
            print("Cancelled by user. Bye!")
            print("--------------------------------")
        finally:
            message = input("Want to try again? (Y/n) ")

    print("Cleaning ended. Bye!")


def main():
    print("##############################################")
    print("Welcome to Elasticsearch cleaning automation. "
          "Please, before proceeding, login to the cluster "
          "as admin using 'oc login'.")
    print("##############################################")

    get_indexes()


if __name__ == '__main__':
    main()
