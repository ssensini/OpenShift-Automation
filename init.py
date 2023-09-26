#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

@author: Claudio Prato & Serena Sensini@Team EA
@created: 2021/04/20
"""

import sys
from argparse import ArgumentParser, ArgumentError, RawDescriptionHelpFormatter
import subprocess
import json


### UTILITIES FUNCTIONS
# START

# Check if a param is empty or blank
def is_empty_or_blank(msg):
    import re
    return re.search("^\s*$", msg)


def lower_output(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).lower()

    return wrapper


def usr_inp(stdout_msg):
    rsp = input(stdout_msg)
    return rsp.strip()


def printflush(text, stream=sys.stdout):
    msg = ''
    stream.write(msg)
    stream.flush()


def runcmd_sh(cmd, obj_to_stdin):

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    p.stdin.write(obj_to_stdin)  # expects a bytes type object
    p_ret = p.communicate()[0]
    p.stdin.close()
    return p.returncode


# Run command with arguments and return its output as a byte string.
# If the return code was non-zero it raises a CalledProcessError
def runcmd_checkoutput(cmd):

    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as suberr:
        p = suberr.returncode
    except Exception as e:
        print(e)
    return p


# Run the command described by args. Wait for command to complete, then return the return code attribute
def runcmd_call(cmd):

    try:
        p = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        return p
    except subprocess.CalledProcessError as error:
        return error.output, error.returncode
    except Exception as e:
        raise Exception(e)

    return p



# END

def parse_args():
    # formatter class
    import textwrap

    args = {'description': textwrap.dedent('''\

    -------------------------------------------------------------------------------
    -- This script would be a shorthand to build, up and push the docker objects --
    -------------------------------------------------------------------------------

    ### AWS SECTION

    # Login and logout docker repository on AWS ECR (the released token is 12 hours valid):
     -------------------------------------------------------------------------------
        ./${script.py} --aws {login|logout} --containerruntime {docker|podman}

    # Remove all the untagged images from a specific AWS ECR repository:
     -------------------------------------------------------------------------------
        ./${script.py} --aws purge-images
        
    # Remove all the untagged images from AWS ECR repository:
    -------------------------------------------------------------------------------
        ./${script.py} --aws purge-images-all
        
    # List all the images from an AWS ECR repository:
     -------------------------------------------------------------------------------
        ./${script.py} --aws list-images

    # Configure a profile under the files /.aws/config and /.aws/credentials
    -------------------------------------------------------------------------------
        ./${script.py} --aws set-profile

    # Get a profile stored under the files /.aws/config and /.aws/credentials
    -------------------------------------------------------------------------------
        ./${script.py} --aws get-profile
        
    # Create repo on ECR for both release and snapshot
    -------------------------------------------------------------------------------
        ./${script.py} --aws create-repo
        
    # Delete repo on ECR
    -------------------------------------------------------------------------------
        ./${script.py} --aws delete-repo

    # Get AWS cli version
    -------------------------------------------------------------------------------
        ./${script.py} --aws version

    ### DOCKER SECTION

    # Get Docker information
    -------------------------------------------------------------------------------
        ./${script.py} --docker {version}
        
    # Pull an image from a registry (Docker or AWS ECR)
    -------------------------------------------------------------------------------
        ./${script.py} --docker {pull}
        
    # Push an image to a registry (Docker or AWS ECR)
    -------------------------------------------------------------------------------
        ./${script.py} --docker {push}
        
    # Tag an image
    -------------------------------------------------------------------------------
        ./${script.py} --docker {tag}
        

    ### PODMAN SECTION

    # Get Podman information
    -------------------------------------------------------------------------------
        ./${script.py} --podman {version}
        
    # Pull an image from a registry (Docker or AWS ECR)
    -------------------------------------------------------------------------------
        ./${script.py} --podman {pull}
        
    # Push an image to a registry (Docker or AWS ECR)
    -------------------------------------------------------------------------------
        ./${script.py} --podman {push}
        
    # Tag an image
    -------------------------------------------------------------------------------
        ./${script.py} --podman {tag}


    ### OPENSHIFT SECTION

    # Get OC client information
    -------------------------------------------------------------------------------
        ./${script.py} --oc {version}

    ### S2I SECTION
    # Get S2I client information
    -------------------------------------------------------------------------------
        ./${script.py} --s2i {version}

    ### TEST environment
    # With this commands, the system will check if all the req are satisfied
    -------------------------------------------------------------------------------
        ./${script.py} --test {system, cluster}


                                                 '''), 'formatter_class': RawDescriptionHelpFormatter}
    parser = ArgumentParser(**args)

    args.clear()
    args['action'] = 'version'
    args['version'] = '1.0'
    args['help'] = 'show program\'s version number and exit'
    parser.add_argument('-v', '--version', **args)
    parser.add_argument('-c', '--containerruntime', help='Set the container runtime', choices=['docker','podman'], default=str('docker'), nargs=1)
    
#    parser.add_argument('action', help='Choice the action', nargs='?', choices=['build', 'up', 'pull'])
    parser.add_argument('--aws', help='AWS ECR functions', nargs=1,
                        choices=['login', 'logout', 'purge-images', 'purge-images-all', 'list-images', 'set-profile', 'get-profile', 'version', 'create-repo', 'delete-repo'])
    parser.add_argument('--docker', help='Docker functions', nargs=1,
                        choices=['version', 'pull', 'push', 'tag'])
    parser.add_argument('--podman', help='Podman functions', nargs=1,
                        choices=['version', 'pull', 'push', 'tag'])
    parser.add_argument('--oc', help='OpenShift CLI functions', nargs=1,
                        choices=['version'])
    parser.add_argument('--test', help='Check whether all the requirements defined in Confluence guide have been '
                                      'implemented', nargs=1,
                        choices=['system', 'cluster'])
    parser.add_argument('--s2i', help='S2I functions', nargs=1,
                        choices=['version'])
  
    # it shows the help if no arguments are passed to script
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        return parser.parse_args()
    except ArgumentError:
        print('''\
        ERROR: option not recognised. Check all the available options by using --help argument.
         -------------------------------------------------------------------------------
        ./${script.py} --help ''')


# Class to manage Docker
class Docker:

    def __init__(self):
        pass

    def get_version(self):
        cmd = ['docker', '--version']

        res = runcmd_call(cmd)
        res = res.strip().replace('Docker version', '')

        version = float(res[0:8].strip()[:5])

        if version < 17.07:
            sys.exit('WARN: The minimum Docker version supported to be able to use AWS-cli is 17.07. Update your '
                     'current version!')
        return version

    def is_installed(self):
        from shutil import which
        return which('docker')

    def pull_image(self):
        image = usr_inp('Insert the image URL you want to pull: ')

        if image != '':
            cmd = ['docker', 'pull', image]

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                if 'access denied' in error_message:
                    print('ERROR: to pull this image, you must login. Use --aws option if is an ECR registry or '
                          '--docker option for a Docker one.')
                elif 'not found' in error_message:
                    print('ERROR: image URL is not correct or it doesn\'t exist. Verify that the repository name is '
                          'correct.')
            else:
                print('Image has been pulled successfully.')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)

    def tag_image(self):
        image_name = usr_inp('Insert the image name you want to tag: ')

        tag = usr_inp('Insert the tag you\'like to add to your image: ')

        registry = usr_inp('Insert the registry (specify a Docker or AWS ECR URL): ')

        if image_name != '' or tag != '' or registry != '':
            cmd = ['docker', 'tag', image_name, registry + '/' + image_name + ':' + tag]

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                if 'not a valid' in error_message:
                    print('ERROR: the provided registry URL is not valid. Check the URL above and verify that its '
                          'syntax is correct.')
                elif 'such image':
                    print('ERROR: the provided image doesn\'t exist. Check the name and retry!')
            else:
                print('Image was tagged successfully!')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)


    def push_image(self):
        image_name = usr_inp('Insert the image name you want to push: ')

        tag = usr_inp('Insert the image tag: ')

        registry = usr_inp('Insert the registry in which you want to push your image (Docker or AWS ECR): ')

        if image_name != '' or tag != '' or registry != '':
            cmd = ['docker', 'push', registry + '/' + image_name + ':' + tag]
            print('\n::: DOCKER PUSH: ' + ' '.join(cmd) + ' ::: \n')

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                print(error_message)
                if 'not a valid' in error_message:
                    print('ERROR: the provided registry URL is not valid. Check the URL above and verify that its '
                          'syntax is correct.')
                elif 'such image':
                    print('ERROR: the provided image doesn\'t exist. Check the name and retry!')
            else:
                print('Image was pushed successfully!')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)

class Podman:

    def __init__(self):
        pass

    def get_version(self):
        cmd = ['podman', '--version']

        res = runcmd_call(cmd)
        res = res.strip().replace('podman version', '')

        version = float(res[0:8].strip()[:3])

        if version < 4.5:
            sys.exit('WARN: The minimum Podman version supported to be able to use AWS-cli is 4.5. Update your '
                     'current version!')
        return version

    def is_installed(self):
        from shutil import which
        return which('podman')

    def pull_image(self):
        image = usr_inp('Insert the image URL you want to pull: ')

        if image != '':
            cmd = ['podman', 'pull', image]

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                if 'access denied' in error_message:
                    print('ERROR: to pull this image, you must login. Use --aws option if is an ECR registry or '
                          '--docker option for a Docker one.')
                elif 'not found' in error_message:
                    print('ERROR: image URL is not correct or it doesn\'t exist. Verify that the repository name is '
                          'correct.')
            else:
                print('Image has been pulled successfully.')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)

    def tag_image(self):
        image_name = usr_inp('Insert the image name you want to tag: ')

        tag = usr_inp('Insert the tag you\'like to add to your image: ')

        registry = usr_inp('Insert the registry (specify a Docker or AWS ECR URL): ')

        if image_name != '' or tag != '' or registry != '':
            cmd = ['podman', 'tag', image_name, registry + '/' + image_name + ':' + tag]

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                if 'not a valid' in error_message:
                    print('ERROR: the provided registry URL is not valid. Check the URL above and verify that its '
                          'syntax is correct.')
                elif 'such image':
                    print('ERROR: the provided image doesn\'t exist. Check the name and retry!')
            else:
                print('Image was tagged successfully!')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)


    def push_image(self):
        image_name = usr_inp('Insert the image name you want to push: ')

        tag = usr_inp('Insert the image tag: ')

        registry = usr_inp('Insert the registry in which you want to push your image (Docker or AWS ECR): ')

        if image_name != '' or tag != '' or registry != '':
            cmd = ['podman', 'push', registry + '/' + image_name + ':' + tag]
            print('\n::: PODMAN PUSH: ' + ' '.join(cmd) + ' ::: \n')

        try:
            res = runcmd_call(cmd)
            if type(res) == tuple and res[1] == 1:
                error_message = res[0].decode()
                print(error_message)
                if 'not a valid' in error_message:
                    print('ERROR: the provided registry URL is not valid. Check the URL above and verify that its '
                          'syntax is correct.')
                elif 'such image':
                    print('ERROR: the provided image doesn\'t exist. Check the name and retry!')
            else:
                print('Image was pushed successfully!')
            sys.exit(0)
        except Exception as e:
            print('ABORT: Error in command running...')
            sys.exit(1)


# Class to manage S2I actions
class S2I:

    def __init__(self):
        pass

    def get_version(self):
        cmd = ['s2i', 'version']
        res = runcmd_call(cmd)
        res = res.strip().replace('s2i ', '')

        version = res[0:6].strip()
        return version

    def is_installed(self):
        from shutil import which
        return which('s2i')


# Class to manage OpenShift client actions
class OC:

    def __init__(self):
        pass

    def get_version(self):
        cmd = ['oc', 'version']

        res = runcmd_call(cmd)
        res = res.strip().replace('oc v', '')

        version = '.'.join(res.split('.', 2)[:2])
        return version

    def is_installed(self):
        from shutil import which
        return which('oc')


# Class to manage AWS actions
class Aws:

    def __init__(self, aws_props_lists=None, aws_prof_name=None, container_runtime=None):
        self.aws_props_lists = aws_props_lists
        self.aws_prof_name = aws_prof_name
        self.container_runtime=container_runtime

    def is_installed(self):
        from shutil import which
        return which('aws')


    def logout(self):
        containerruntime = self.container_runtime
        cmd = [containerruntime, 'logout', '350801433917.dkr.ecr.eu-west-1.amazonaws.com']
        print('\n::: AWS LOGOUT: ' + ' '.join(cmd) + ' ::: \n')
        result = runcmd_call(cmd)
        print(result)
        sys.exit(0)


    def login(self):
        try:
            # setting the command string depends to profile
            props = dict(self.aws_props_lists)
            region = props['region']
            profile = self.aws_prof_name
            containerruntime = self.container_runtime
            cmd = ['aws', 'ecr', 'get-login-password', '--region', region, '--profile', profile]
            print('\n::: GET-LOGIN: ' + ' '.join(cmd) + ' ::: \n')

            token = runcmd_call(cmd)

            # Execute the docker Login by security token
            cmd = [containerruntime, 'login', '-u', 'AWS', '--password-stdin',
                   '350801433917.dkr.ecr.eu-west-1.amazonaws.com']
            print('\n::: ' + containerruntime.upper() + ': ' + ' '.join(cmd) + ' ::: \n')
            
            returncode=runcmd_sh(cmd,token)
            
            # When using podman there is no daemon, it depends on the VM being started, although NOT definitive 125 return code
            #  often coincides that the user has not started the machine with 'podman machine start', so give a hint.
            if (returncode==125 and containerruntime=='podman') :
                print('ERROR: connection could not be made, is it possible your podman VM is NOT running?  If so please run "podman machine start"')
            elif returncode==0:
                print('SUCCESS: Logged in')
            return returncode
        except FileNotFoundError as err:
            print('ERROR: The login procedure failed.  Check you have Docker or Podman installed, if not Docker reference podman with the "--containerruntime podman" parameter')
            sys.exit(2)
        except Exception as err:
            print('ERROR: The login procedure is failed. Check the credentials and retry!::')
            sys.exit(1)


    def purge_images(self):

        rsp = usr_inp('Do you want to delete UNTAGGED images or a specific one?[untagged|single] ') or 'untagged'

        if rsp == 'untagged':
            # To delete all untagged images
            rsp = usr_inp('Are you sure to delete all untagged images on AWS ECR repository?[yes|NO] ') or 'no'
            if rsp == 'yes':
                repo = usr_inp('Enter the repository name: ')
                profile = self.aws_prof_name
                if repo != '' and profile != '':
                    cmd = ['aws', 'ecr', 'list-images', '--repository-name', repo, '--profile', profile, '--filter',
                           'tagStatus=UNTAGGED', '--query', 'imageIds[*]', '--output', 'text']
                print('INFO: Removing the untagged images on AWS ECR repository')
            else:
                print('ABORT: User denied...')
                sys.exit(1)

            debug_msg = '::: LIST-IMAGES: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            untagged_images = runcmd_checkoutput(cmd)
            if type(untagged_images) == int:
                print('ERROR: Error during the purge: check the repository information!')
                print('Code: ' + str(untagged_images))
                print('''
                    Checkout the documentation for AWS cli: '
                      'https://docs.aws.amazon.com/cli/latest/topic/return-codes.html
                      ''')
                return -1
            else:
                untagged_images = untagged_images.decode()
                untagged_images = untagged_images.rstrip().split('\n')

            if len(untagged_images) > 0 and untagged_images[0] != '':
                for image in untagged_images:
                    cmd = ['aws', 'ecr', 'batch-delete-image', '--profile', profile, '--repository-name', repo,
                           '--image-ids', 'imageDigest=' + image]
                    debug_msg = '::: PURGE: ' + ' '.join(cmd) + ' ::: \n'
                    print(debug_msg)
                    res = runcmd_checkoutput(cmd)
                    if type(res) == int:
                        print('ERROR: Error during the purge!')
                        print('Error code: ' + str(res))
                        print('Checkout the documentation for AWS cli 2: '
                              'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                        break
                    else:
                        continue
                print("COMPLETED!")
            else:
                print('INFO: Congrats. There are no untagged images in the specified repository!')
            return 0

        elif rsp == 'single':
            # To delete a specified image

            repo = usr_inp('Enter the repository name: ')
            if repo != '':
                tag = usr_inp('Insert the desidered tag: ') or ''
                profile = self.aws_prof_name
                if tag != '' and profile != '':
                    cmd = ['aws', 'ecr', 'batch-delete-image', '--profile', profile, '--repository-name', repo,
                           '--image-ids', 'imageTag=' + tag]
                    debug_msg = '::: PURGE: ' + ' '.join(cmd) + ' ::: \n'
                    print(debug_msg)
                    res = runcmd_checkoutput(cmd)
                    if type(res) == int:
                        print('ERROR: Error during the purge!')
                        print('Error code: ' + str(res))
                        print('Checkout the documentation for AWS cli 2: '
                              'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                    else:
                        print('INFO: Congrats. Specified image has been deleted!')
            else:
                print('ABORT: User denied...')
                sys.exit(1)

            return 0

    def purge_images_all(self):

        # To delete all untagged images
        rsp = usr_inp('Are you sure to delete all untagged images on any AWS ECR repository?[yes|NO] ') or 'no'
        if rsp == 'yes':
            cmd = ['aws', 'ecr', 'describe-repositories']
            print('INFO: Retrieving all repos...')
        else:
            print('ABORT: User denied...')
            sys.exit(1)

        debug_msg = '::: LIST-REPOS: ' + ' '.join(cmd) + ' ::: \n'

        print(debug_msg)

        response = runcmd_checkoutput(cmd)

        if type(response) == int:
            print('ERROR: Error during execution!')
            print('Code: ' + str(response))
            print('''
                Checkout the documentation for AWS cli: '
                  'https://docs.aws.amazon.com/cli/latest/topic/return-codes.html
                  ''')
            return -1
        else:
            response = response.decode()

        to_dict = json.loads(response)
        repositories = to_dict['repositories']
        list_repo_names = []

        # List all ECR repos
        for repo in repositories:
            # Filter for snapshot ones (release ones can't contain untagged images)
            if "snapshot" in repo['repositoryName'].lower():
                list_repo_names.append(repo['repositoryName'])

        profile = self.aws_prof_name

        total_count = 0
        # Retrieve all untagged images for each repo
        for repo in list_repo_names:
            print("###################### REPO:", repo)
            print()
            cmd = ['aws', 'ecr', 'list-images', '--repository-name', repo, '--profile', profile, '--filter',
                   'tagStatus=UNTAGGED', '--query', 'imageIds[*]', '--output', 'text']

            debug_msg = '::: LIST-IMAGES: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            untagged_images = runcmd_checkoutput(cmd)
            if type(untagged_images) == int:
                print('ERROR: Error during the purge: check the repository information or permissions!')
                print('Code: ' + str(untagged_images))
                print('''
                                Checkout the documentation for AWS cli: '
                                  'https://docs.aws.amazon.com/cli/latest/topic/return-codes.html
                                  ''')
                continue
                # return -1
            else:
                untagged_images = untagged_images.decode()
                untagged_images = untagged_images.rstrip().split('\n')

            if len(untagged_images) > 0 and untagged_images[0] != '':
                print("######### Untagged images count: ", len(untagged_images))
                print()
                total_count += len(untagged_images)
                # with open("logs/purge.log", "w+") as file:
                for image in untagged_images:
                    cmd = ['aws', 'ecr', 'batch-delete-image', '--profile', profile, '--repository-name', repo,
                           '--image-ids', 'imageDigest=' + image]
                    debug_msg = '::: PURGE: ' + ' '.join(cmd) + ' ::: \n'
                    print(debug_msg)
                    # file.write(debug_msg)
                    res = runcmd_checkoutput(cmd)
                    if type(res) == int:
                        print('ERROR: Error during this purge! Keep note of the repository and verify later.')
                        print('Error code: ' + str(res))
                        print('Checkout the documentation for AWS cli 2: '
                              'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                        # break
                    # else:
                        continue
            else:
                print('INFO: Congrats. There are no untagged images in the specified repository!')
                print()
                # file.close()
        print("Purge completed! You successfully deleted", total_count, "images in your ECR registry.")


    def set_profile(self):
        rsp = usr_inp('Are you sure to configure a profile?[yes|NO]') or 'no'
        if rsp == 'yes':
            profile_name = usr_inp('Insert a profile name: ')
            access_key_id = usr_inp('Insert the AWS Access Key ID: ')
            access_secret_key = usr_inp('Insert the AWS Secret Access Key: ')

            region = usr_inp('Insert a default region: ')
            output = usr_inp('Insert a default output type: ')

            params = []
            params.append(profile_name)
            params.append(access_key_id)
            params.append(access_secret_key)
            params.append(region)
            params.append(output)

            result = any([is_empty_or_blank(elem) for elem in params])
            if result:
                print('ERROR: One or more params are empty. Cannot complete the configuration of the profile!')
                sys.exit(1)
            else:
                cmd = ['aws', 'configure', 'set', 'aws_access_key_id', access_key_id, '--profile', profile_name]

                print('\n::: ' + ' '.join(cmd) + ' ::: \n')
                print(runcmd_call(cmd))

                cmd = ['aws', 'configure', 'set', 'aws_secret_access_key', access_secret_key, '--profile', profile_name]

                print('\n::: ' + ' '.join(cmd) + ' ::: \n')
                print(runcmd_call(cmd))

                cmd = ['aws', 'configure', 'set', 'region', region, '--profile', profile_name]

                print('\n::: ' + ' '.join(cmd) + ' ::: \n')
                print(runcmd_call(cmd))

                cmd = ['aws', 'configure', 'set', 'output', output, '--profile', profile_name]

                print('\n::: ' + ' '.join(cmd) + ' ::: \n')
                print(runcmd_call(cmd))

                print('INFO: Profile configured successfully!')
                sys.exit(0)
        else:
            print('ABORT: Failed to set the profile...')
            sys.exit(1)

    def get_profile_info(self):
        try:
            profile_name = usr_inp('Insert the profile\'s name you would like to use: ')
            cmd = ['aws', 'configure', 'get', 'aws_access_key_id', '--profile', profile_name]
            access_key = (runcmd_checkoutput(cmd))
            if type(access_key) == int:
                print("ERROR: The specified AWS profile is not configured. Use '--aws set-profile' to set a new one.")
                sys.exit(0)

            cmd = ['aws', 'configure', 'get', 'aws_secret_access_key', '--profile', profile_name]
            secret_key = (runcmd_call(cmd))

            cmd = ['aws', 'configure', 'get', 'region', '--profile', profile_name]
            region = (runcmd_call(cmd).decode())

            cmd = ['aws', 'configure', 'get', 'output', '--profile', profile_name]
            output = (runcmd_call(cmd))
            self.aws_prof_name = profile_name
            self.aws_props_lists = [('aws_access_key_id', access_key.strip()), \
                                    ('aws_secret_access_key', secret_key.strip()), \
                                    ('region', region.strip()), \
                                    ('output', output.strip())]
            print(self.aws_props_lists)
        except:
            print("ERROR: The specified AWS profile is not configured. Use '--aws set-profile' to set a new one.")
            sys.exit(0)

    def get_available_profiles(self):
        cmd = ['aws', 'configure', 'list']
        print('\n::: ' + ' '.join(cmd) + ' ::: \n')
        return runcmd_call(cmd)

    def get_version(self):
        cmd = ['aws', '--version']

        res = runcmd_checkoutput(cmd).decode()
        index_vers = res.strip().index('Python')

        substr = res[:index_vers]

        version = substr.replace('aws-cli/', '')
        version = '.'.join(version.split('.', 2)[:2])
        return float(version)

    def list_images(self):

        repo = usr_inp('Enter the repository name: ')
        profile = self.aws_prof_name
        if repo != '' and profile != '':
            cmd = ['aws', 'ecr', 'list-images', '--repository-name', repo, '--profile', profile, '--output', 'json']

            debug_msg = '::: LIST-IMAGES: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            res = runcmd_checkoutput(cmd)
            if type(res) == int:
                print('ERROR: Error while retrieving the images!')
                print('Error code: ' + str(res))
                print('Checkout the documentation for AWS cli 2: '
                      'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                sys.exit(0)
            else:
                images = res.decode()
                print(images)
                sys.exit(0)

    def create_repo(self):
        print("This command will allow you to create a repo on ECR for both release and snapshot images.")
        print("According to your input, two repos will be created, where one has '-snapshot' as suffix, as explained in the documentation (link: https://confluence.dedalus.com/display/DRA/OCP+-+1+-+S2I+Quick+Start). ")
        print("Example: the input is 'products/organization_name/my_product'")
        print("Result: 'products/organization_name/my_product' and 'products/organization_name/my_product-snapshot' created.")
        repo = usr_inp('Enter the repository name: ')
        profile = self.aws_prof_name
        if repo != '' and profile != '':
            # release repo
            cmd = ['aws', 'ecr', 'create-repository', '--repository-name', repo, '--image-tag-mutability', 'IMMUTABLE', '--image-scanning-configuration', 'scanOnPush=true']

            debug_msg = '::: CREATE-REPO FOR RELEASE: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            res = runcmd_checkoutput(cmd)
            if type(res) == int:
                print('ERROR: Error while creating the repos!')
                print('Error code: ' + str(res))
                print('Checkout the documentation for AWS cli 2: '
                      'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                # sys.exit(0)
            else:
                images = res.decode()
                print(images)
                # sys.exit(0)

            cmd = ['aws', 'ecr', 'create-repository', '--repository-name', repo+'-snapshot', '--image-tag-mutability', 'MUTABLE',
                   '--image-scanning-configuration', 'scanOnPush=true']

            # snapshot repo
            debug_msg = '::: CREATE-REPO FOR SNAPSHOT: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            res = runcmd_checkoutput(cmd)
            if type(res) == int:
                print('ERROR: Error while creating the repos!')
                print('Error code: ' + str(res))
                print('Checkout the documentation for AWS cli 2: '
                      'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                sys.exit(0)
            else:
                images = res.decode()
                print(images)
                sys.exit(0)
        pass

    def delete_repo(self):
        repo = usr_inp('Enter the repository name: ')

        snapshot = usr_inp('Do you want to remove the snapshot repo too? Y/n - ')
        profile = self.aws_prof_name
        print(profile)
        if repo != '' and profile != '':
            cmd = ['aws', 'ecr', 'delete-repository', '--repository-name', repo, '--profile', profile, '--output', 'json']

            debug_msg = '::: REMOVE-REPO for RELEASE: ' + ' '.join(cmd) + ' ::: \n'
            print(debug_msg)
            res = runcmd_call(cmd)
            if type(res[1]) == int:
                message = res[0].decode("utf-8")
                print('ERROR: Error while removing the repository!')
                print('Error code: ' + str(res[1]))
                print('Error message:' + message)
                print('Checkout the documentation for AWS cli 2: '
                      'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                sys.exit(0)
            else:
                images = res.decode()
                print(images)
                # sys.exit(0)

            if snapshot.lower() == 'y':
                cmd = ['aws', 'ecr', 'delete-repository', '--repository-name', repo+'-snapshot', '--profile', profile, '--output',
                       'json']

                debug_msg = '::: REMOVE-REPO for SNAPSHOT: ' + ' '.join(cmd) + ' ::: \n'
                print(debug_msg)
                res = runcmd_call(cmd)
                if type(str(res[1])) == int:
                    message = res[0].decode("utf-8")
                    print('ERROR: Error while removing the repository!')
                    print('Error code: ' + str(res[1]))
                    print('Error message:' + message)
                    print('Checkout the documentation for AWS cli 2: '
                          'https://awscli.amazonaws.com/v2/documentation/api/latest/topic/return-codes.html')
                    sys.exit(0)
                else:
                    images = res.decode()
                    print(images)
                    sys.exit(0)

### END of the AWS class

# Factory to redirect commands to proper functions
def main():
    # Get the command line options
    args = parse_args()

    printflush('DEBUG: the arguments values are: ' + str(args) + '\n')

    # Manages the --aws arguments
    try:
        if args.aws:
            if type(args.containerruntime)==list:
                runtime=args.containerruntime[0]
            else:
                runtime=args.containerruntime
            
            aws = Aws(container_runtime=runtime)
            if aws.is_installed():

                # check which version is installed
                if 1.0 <= aws.get_version() <= 2.0:
                    print('''
                        -------------------------------------------------------------------------------
                        Note: AWS CLI version 2, the latest major version of the AWS CLI, is now stable and recommended 
                        for general use. For more information, see the AWS CLI version 2 installation instructions at: 
                        https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html 
                        -------------------------------------------------------------------------------
                        ''')

                # check if input needs profile's info
                if args.aws[0] in ['login', 'purge-images', 'purge-images-all', 'list-images', 'create-repo', 'delete-repo']:
                    aws.get_profile_info()

                if args.aws[0] == 'login':
                    aws.login()
                elif args.aws[0] == 'logout':
                    aws.logout()
                elif args.aws[0] == 'purge-images':
                    aws.purge_images()
                elif args.aws[0] == 'purge-images-all':
                    aws.purge_images_all()
                elif args.aws[0] == 'set-profile':
                    aws.set_profile()
                elif args.aws[0] == 'get-profile':
                    aws.get_profile_info()
                elif args.aws[0] == 'version':
                    print(aws.get_version())
                elif args.aws[0] == 'list-images':
                    print(aws.list_images())
                elif args.aws[0] == 'create-repo':
                    print(aws.create_repo())
                elif args.aws[0] == 'delete-repo':
                    print(aws.delete_repo())

            else:
                print('''
                -- AWS --
                -------------------------------------------------------------------------------
                Result: KO
                Details: AWS-cli is not installed in the current system. To install it, check this link:
                  https://docs.aws.amazon.com/en_us/cli/latest/userguide/install-cliv2.html

                -------------------------------------------------------------------------------
                ''')

        elif args.docker:
            docker = Docker()
            if docker.is_installed():

                if args.docker[0] == 'version':
                    print(docker.get_version())

                if args.docker[0] == 'pull':
                    print(docker.pull_image())

                if args.docker[0] == 'tag':
                    print(docker.tag_image())

                if args.docker[0] == 'push':
                    print(docker.push_image())

            else:
                print('''\
                    -------------------------------------------------------------------------------
                    -- Docker --
                    -------------------------------------------------------------------------------
                    Result: KO
                    Details: Docker is not installed in the current system. To install it, check this link: 
                      https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository
                ''')

        elif args.podman:
            podman = Podman()
            if podman.is_installed():

                if args.podman[0] == 'version':
                    print(podman.get_version())

                if args.podman[0] == 'pull':
                    print(podman.pull_image())

                if args.podman[0] == 'tag':
                    print(podman.tag_image())

                if args.podman[0] == 'push':
                    print(podman.push_image())

            else:
                print('''\
                    -------------------------------------------------------------------------------
                    -- Podman --
                    -------------------------------------------------------------------------------
                    Result: KO
                    Details: Podman is not installed in the current system. To install it, check this link: 
                      https://podman.io/docs/installation
                ''')

        elif args.oc:
            oc = OC()

            if oc.is_installed():

                if args.oc[0] == 'version':
                    print(oc.get_version())

            else:
                print('''\
                       -------------------------------------------------------------------------------
                       -- OpenShift Cluster --
                       -------------------------------------------------------------------------------
                       Result: KO
                       Details: OpenShift Cluster is not installed. To download it, check the link: https://www.okd.io/download.html
                   ''')

        elif args.test:
            s2i = S2I()
            aws = Aws()
            container_runtime=args.containerruntime
            docker = Docker()
            podman = Podman()
            oc = OC()
            passed = True

            print('''\
                -------------------------------------------------------------------------------
                -- This test will check if all the requirements are satisfied. --
                -------------------------------------------------------------------------------
                ''')
            if args.test[0] == 'system':
                if s2i.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- S2I --
                -------------------------------------------------------------------------------
                Result: KO
                Details: S2I is not installed in the current system. To install it, check this link: 
                  'https://github.com/openshift/source-to-image#for-linux
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- S2I --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if aws.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: KO
                Details: AWS-cli is not installed in the current system. To install it, check this link: 
                  https://docs.aws.amazon.com/en_us/cli/latest/userguide/install-cliv2.html
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'docker' and docker.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Docker is not installed in the current system. To install it, check this link: 
                  https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'podman' and podman.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Podman is not installed in the current system. To install it, check this link: 
                  https://podman.io/docs/installation
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if passed:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: OK
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Some requirements are missing or are not configure properly. Check the 
                logs before.
                ''')
                sys.exit(0)
            elif args.test[0] == 'cluster':
                if oc.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- OpenShift Cluster --
                -------------------------------------------------------------------------------
                Result: KO
                Details: OpenShift Cluster is not installed. To download it, check the link: https://www.okd.io/download.html
                ''')
                elif float(oc.get_version()) < 3.9 or docker.get_version() != 1.13:
                    passed = False
                    print('''\
                --------------------------------------------------------------------------------- 
                -- OpenShift --
                ---------------------------------------------------------------------------------
                Result: KO Details: To run an OpenShift cluster locally, you must have a compatible version of Docker 
                installed in your environment. OpenShift officially supports the following versions of Docker: 
                |-------------------|----------------|
                | OpenShift version | Docker version |
                |-------------------|----------------|
                | 3.9+              | 1.13           |
                | 3.6-3.7           | 1.12           |
                | 1.4-1.5           | 1.12           |
                |-------------------|----------------|
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- OpenShift --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if aws.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: KO
                Details: AWS-cli is not installed in the current system. To install it, check this link: 
                  https://docs.aws.amazon.com/en_us/cli/latest/userguide/install-cliv2.html
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'docker' and docker.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Docker is not installed in the current system. To install it, check this link: 
                  https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'podman' and podman.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Podman is not installed in the current system. To install it, check this link: 
                  https://podman.io/docs/installation
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if passed:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: OK
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Some requirements are missing or are not configure properly. Check the 
                logs before.
                ''')
                sys.exit(0)

        elif args.s2i:
            s2i = S2I()

            if s2i.is_installed():
                if args.s2i[0] == 'version':
                    print(s2i.get_version())
            else:
                print('''\
                    -------------------------------------------------------------------------------
                    -- S2I --
                    -------------------------------------------------------------------------------
                    Result: KO
                    Details: S2I is not installed in the current system. To install it, check this link: 
                      'https://github.com/openshift/source-to-image#for-linux
                    ''')

        elif args.test:
            s2i = S2I()
            aws = Aws()
            docker = Docker()
            podman = Podman()
            oc = OC()
            passed = True

            print('''\
                -------------------------------------------------------------------------------
                -- This test will check if all the requirements are satisfied. --
                -------------------------------------------------------------------------------
                ''')
            if args.test[0] == 'system':
                if s2i.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- S2I --
                -------------------------------------------------------------------------------
                Result: KO
                Details: S2I is not installed in the current system. To install it, check this link: 
                  'https://github.com/openshift/source-to-image#for-linux
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- S2I --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if aws.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: KO
                Details: AWS-cli is not installed in the current system. To install it, check this link: 
                  https://docs.aws.amazon.com/en_us/cli/latest/userguide/install-cliv2.html
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'docker' and docker.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Docker is not installed in the current system. To install it, check this link: 
                  https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'podman' and podman.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Podman is not installed in the current system. To install it, check this link: 
                  https://podman.io/docs/installation
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if passed:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: OK
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Some requirements are missing or are not configure properly. Check the 
                logs before.
                ''')
                sys.exit(0)
            elif args.test[0] == 'cluster':
                if oc.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- OpenShift Cluster --
                -------------------------------------------------------------------------------
                Result: KO
                Details: OpenShift Cluster is not installed. To download it, check the link: https://www.okd.io/download.html
                ''')
                elif float(oc.get_version()) < 3.9 or docker.get_version() != 1.13:
                    passed = False
                    print('''\
                --------------------------------------------------------------------------------- 
                -- OpenShift --
                ---------------------------------------------------------------------------------
                Result: KO Details: To run an OpenShift cluster locally, you must have a compatible version of Docker 
                installed in your environment. OpenShift officially supports the following versions of Docker: 
                |-------------------|----------------|
                | OpenShift version | Docker version |
                |-------------------|----------------|
                | 3.9+              | 1.13           |
                | 3.6-3.7           | 1.12           |
                | 1.4-1.5           | 1.12           |
                |-------------------|----------------|
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- OpenShift --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if aws.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: KO
                Details: AWS-cli is not installed in the current system. To install it, check this link: 
                  https://docs.aws.amazon.com/en_us/cli/latest/userguide/install-cliv2.html
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- AWS --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'docker' and docker.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Docker is not installed in the current system. To install it, check this link: 
                  https://docs.docker.com/install/linux/docker-ce/centos/#install-using-the-repository
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Docker --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if container_runtime == 'podman' and podman.is_installed() is None:
                    passed = False
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Podman is not installed in the current system. To install it, check this link: 
                  https://podman.io/docs/installation
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- Podman --
                -------------------------------------------------------------------------------
                Result: OK
                ''')

                if passed:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: OK
                ''')
                else:
                    print('''\
                -------------------------------------------------------------------------------
                -- FINAL RESULT --
                -------------------------------------------------------------------------------
                Result: KO
                Details: Some requirements are missing or are not configure properly. Check the 
                logs before.
                ''')
                sys.exit(0)

    except:
        pass


if __name__ == '__main__':
    main()
