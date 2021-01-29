# The ccloud client container installer script

This tool has been tested to work with the Catalyst Cloud Openstack implementation, feel free to
take your own copy and make it work for the cloud vendor of your choice.

## Just Give Me The Tools!
If all you really care about is getting your hands on a working version of the container then
simply run the following install command from a Linux shell to have a copy installed locally.

> Note:
  This tool has the following pre-requisites:
  - docker
  - python > 3.8.x

*OpenStackClient container install command*

<a name="install-command-wget">

```
python <(wget -qO - https://raw.githubusercontent.com/chelios/python-ccloud-client/master/fetch-installer.py) -a ccloud -u https://api.cloud.catalyst.net.nz:5000/v3
```
</a>

<a name="install-command-curl">

```
python <(curl -s - https://raw.githubusercontent.com/chelios/python-ccloud-client/master/fetch-installer.py) -a ccloud -u https://api.cloud.catalyst.net.nz:5000/v3
```
</a>

## Overview
To provide the Catalyst Cloud command line tools pre-installed, with all of it's dependencies, in a
docker container.

### The Installer Script
The purpose of this script (__fetch-installer.py__) is to simplify the process of obtaining and
configuring the Catalyst Cloud container. The command shown below is going to download a copy of
the installer script to the user's machine and run it. That script, in turn, creates a launcher
script and places a copy in the directory specified by the user, creating this directory in the
process if it does not already exist.

Finally it adds an alias in the user's .bash_aliases file to allow them to run commands and pass
them directly to the [OpenStackClient](https://docs.openstack.org/python-openstackclient/latest/)
command line tool.

#### Using The Alias
Here is an example of the _default_ alias created by the installer script in the .bash_aliases
file:

```
alias ccloud='<install_dir>/ccloud-client'
```
A typical openstack command looks something like this:

```
openstack server list
```

The alias created by the script takes the place of openstack keyword in the command shown above.
To run a command through the ccloud client within the container the format would be like this:

```
ccloud server list
```

This is done in order to differentiate calls to the container versus calls to a locally installed
version of the openstack client, should one exist.

### The Launcher Script
This script (__ccloud-client-install.py__) provides a means to launch a pre-configured docker
container that will provide the user with a working instance of the Catalyst Cloud command line
tools. The script performs the following actions:

- asks for an installation directory, the default is $HOME
- checks for a valid docker installation, see [install docker](https://docs.docker.com/install/)
  for OS specific steps.
- retrieves the latest version of the **ccloud client** container, if a copy exists locally it
  will be used first, if it is the latest stable version.
- ensuring that valid Catalyst Cloud credentials are available by checking the current shell for
- existing OpenStack authentication environment variables.


  __NOTE:__ if the user is prompted to provide their credentials these details, along with the
  initial choice of cloud region and cloud project, will be stored in local configuration files
  n plaint text.

#### Launcher configuration

The installer script currently allows the user to provide two additional parameters when being
invoked. To use the parameters described below simply append them to the end of the
[install command](#install-command) leaving one space after the closing parentheses as shown here.

The parameters support both short and long forms.

```
bash <(wget https://install-file-location) --parameter parameter-value
```

###### Specifying the tool alias

The first is the alias name that will be used to invoke the tool once it is installed. By default
this is set to be ``osc``. In order to override this append the following parameter followed by
your preferred alias name.

```
-a your-alias
```
or
```
--alias your-alias
```

###### Specifying the AUTH_URL

The second variable to be aware of is the AUTH_URL value that will connect you to your OpenStack
cloud provider. This currently defaults to Catalyst Cloud if none is provided at install time.

```
-u https://an.openstack.vendor:5000
```
or
```
--url https://an.openstack.vendor:5000
```

#### Credential management

In order to run the tools first source your *-openrc.sh file in the current terminal session prior
to running any **ccloud** commands

```
Note:
At the current time this tool only supports v3 of the keystone identity service.

```
