# EA Utilities
## Scope
Validate if all the requirements for OpenShift installations described in [this](https://confluence.dedalus.com/display/AF/OCP+-+1+-+S2I+Quick+Start#) 
guide are accomplished and correctly configured, manage AWS services through the CLI and manage cluster's tools, such as Elasticsearch. 

## Installation

Clone this project or just download the `.*py` file.

## Requirements
- Python 3.x+

## Usage

```bash
$ python3 init.py # for AWS, Docker and OpenShift management
$ python3 es.py # for Elasticsearch indexes cleaning (WIP)
```

## Available options for init.py:

| Option                                                                                                                 | Description                                                                                                                                                         |
|------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| --help                                                                                                                 | Get all the available options                                                                                                                                       |
| --version                                                                                                              | Show program's version                                                                                                                                              |
| --aws {login,logout,set-profile,get-profile,purge-images,purge-images-all,list-images,version,create-repo,delete-repo} | AWS CLI _login_ and _logout_ functions, _purge_-_images_ on a specified AWS repo and profile configuration, _create_-_repo_ and _delete_-_repo_ to manage ECR repos |
| --docker {version}                                                                                                     | Docker CLI functions                                                                                                                                                |
| --oc {version}                                                                                                         | OpenShift CLI functions                                                                                                                                             |
| --s2i {version}                                                                                                        | S2I CLI functions                                                                                                                                                   |
| --test {system,cluster}                         <br/>                                                                  | Check whether all the requirements have been implemented, depending if you want to test your local system or a cluster solution                                     |

For more information on the commands and options, run the following:

```bash
python3 init.py --help
```

# TODO tasks

- Adding Podman support
