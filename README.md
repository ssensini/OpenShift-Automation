# Openshift support tools

## Scope

Different Python scripts are provided to help with the OpenShift management:

- _init.py_: validate if all the requirements described in [this](https://confluence.dedalus.eu/display/AF/OCP+-+1+-+S2I+Quick+Start#) guide are accomplished and correctly configured and manage cluster's tools, such as Elasticsearch.
- _es.py_: manage indexes for ElasticSearch installation. 

## Installation

Clone this project or just download the `.*py` file.

## Requirements
- Python 3.x+

## Usage

```
$ python3 init.py # for AWS, Docker and OpenShift management
$ python3 es.py # for Elasticsearch indexes cleaning
```

## Available options for init.py:

| Option                                                                                   | Description                                                                                                                     |
|------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| --help                                                                                   | Get all the available options                                                                                                   |
| --version                                                                                | Show program's version                                                                                                          |
| --aws {login,logout,purgeimages,set-profile,get-profile,purgeimages,listimages,version}  | AWS CLI login and logout functions, purge images on a specified AWS repo and profile configuration                              |
| --docker {version}                                                                       | Docker CLI functions                                                                                                            |
| --oc {version}                                                                           | OpenShift CLI functions                                                                                                         |
| --s2i {version}                                                                          | S2I CLI functions                                                                                                               |
| --test {system,cluster}                                                                  | Check whether all the requirements have been implemented, depending if you want to test your local system or a cluster solution |
