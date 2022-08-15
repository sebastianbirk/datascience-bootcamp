# 1. Bootcamp Introduction, Tools Setup & Python Introduction

## 1.1 Bootcamp Introduction

The bootcamp introduction presentation is available [here](https://github.com/sebastianbirk/datascience-bootcamp/blob/main/content/01_bootcamp_intro_tools_setup_%26_python_intro/1.1_bootcamp_introduction.pptx).

## 1.2 Tools Setup

Before we start the deep dive into the data-related topics of the data science bootcamp, we will install all required tools on our system and at the same time familiarize ourselves with a chosen subset of the landscape of commonly used data science tools (**Note**: here we assume that you are working with a Windows OS; steps will deviate if you have MacOS or a Linux distribution). While the landscape of data science tools is very diverse nowadays, we will cover some of the most well known and useful tools including:
- Windows Subystem for Linux (WSL)
- Windows Terminal
- Git
- Miniconda / Conda & Python
- Visual Studio Code
- JupyterLab

In addition to these tools, which we will install locally, you will also need an Azure subscription with some credits. You can get an Azure subscription with credits e.g. through a Visual Studio Professional Subscripton ($50 monthly credit) or a Visual Studio Enterprise Subscription ($150 monthly credit). The credits will be needed for session 8 "Applied Data Science with Azure" and session 9 "Distributed Computing & Spark". If you are an Avanadee, and you do not have a Visual Studio Professional or Enterprise subscription yet, you can go to the Support Portal and search for "Visual Studio Subscriptions". There you will find instructions on how to request a subscription.

**Note**: It is recommended to use your local workstation for the data science bootcamp. However, If you have an Azure subscription with credits, you can also create an Ubuntu 18.04 Virtual Machine in the Azure cloud and use that as an alternative to your local workstation for the data science bootcamp. In this case, the Windows Subsystem for Linux (WSL) and the Windows Terminal sections will be irrelevant for you and you can skip these sections. For the Visual Studio Code section, you can just install and use Visual Studio Code and you will not need the Remote Development extension.

Only if you want to use an Azure VM instead of your local workstation, follow below steps. Otherwise skip to section 1.2.1:

- Deploy the Ubuntu 18.04 VM in your Azure subscription:
    - [![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsebastianbirk%2Fdatascience-bootcamp%2Fmain%2Finfrastructure%2Fvm%2Ftemplate.json)
        - Create a new resource group called "datasciencebootcamp".
        - Make sure to choose your own password before creating the resource and be aware that in a production scenario SSH keys would be the preferred authentication method and password should not be used (**Note**: If you are interested in learning more about Azure Deployment Buttons, check this out: https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-to-azure-button).
    - After your Virtual Machine is deployed, you can access it by opening the Command Prompt from your Windows machine and typing:
ssh server-admin@<DNS_NAME> where you can find the <DNS_NAME> on the Overview page of your Virtual Machine in the Azure Portal.

### 1.2.1 Windows Subsystem for Linux (WSL)

WSL enables us to use a Linux distribution operating system with Linux tools on our Windows machines in a completely integrated manner (no need to dual-boot).
When we install a Linux distribution with WSL, we are installing a new file system, separated from the Windows NTFS C:\ drive.

**Documentation**: [https://docs.microsoft.com/en-us/windows/wsl/](https://docs.microsoft.com/en-us/windows/wsl/)

#### 1.2.1.1 Install WSL

**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/install](https://docs.microsoft.com/en-us/windows/wsl/install)

- Open PowerShell or Windows Command Prompt in administrator mode and run
```wsl --install -d Ubuntu``` (this will install WSL together with an Ubuntu distribution, which is also the default). Reboot may be required to make the installation take effect.
- Once you have installed WSL, open Ubuntu from the Windows start menu (if it has not opened automatically after installation). We can also pin Ubuntu to our Windows taskbar for easy accessibility in the future. 
- You will now be prompted to create a user account and password for your newly installed Linux distribution. This account will be considered the Linux administrator, with the ability to run sudo (Super User Do) administrative commands.
- We can now interact with our Ubuntu distribution through the bash console that was launched.

#### 1.2.1.2 Set up a WSL development environment

**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/setup/environment#set-up-your-linux-username-and-password](https://docs.microsoft.com/en-us/windows/wsl/setup/environment)

- Upgrade your packages using the apt package manager by running ```sudo apt update && sudo apt upgrade``` in the launched bash console.
- We can open the new file system that comes with our Ubuntu distribution by leveraging the Windows explorer. To do this, enter the home directory and start the explorer executable from your Bash console as follows:
```cd ~```
```explorer.exe .```

### 1.2.2 Windows Terminal

Windows Terminal is a modern application that allows the use of many command-line shells like Command Prompt, PowerShell and bash (via Windows Subsystem for Linux) in a beautiful customizable terminal with features such as multiple tabs and panes, Unicode and UTF-8 character support and a GPU accelerated text rendering engine.

**Documentation**: [https://docs.microsoft.com/en-us/windows/terminal/](https://docs.microsoft.com/en-us/windows/terminal/)

#### 1.2.2.1 Install Windows Terminal from the Microsoft Store
**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/terminal/install](https://docs.microsoft.com/en-us/windows/terminal/install)

- Install Windows Terminal from the Microsoft Store by following this link: [https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=de-de&gl=DE](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=de-de&gl=DE).
- Once Windows Terminal is installed, search for Terminal in the Windows start menu and start the application. We can also pin Terminal to our Windows taskbar for easy accessibility in the future.

#### 1.2.2.2 Set up Windows Terminal

- Configure "Ubuntu" as your Startup Default profile as described in [https://docs.microsoft.com/en-us/windows/terminal/install#set-your-default-terminal-profile](https://docs.microsoft.com/en-us/windows/terminal/install#set-your-default-terminal-profile).

### 1.2.3 Git

Git enables us to version control our files and track changes so that we have a nicely structured recorded history and don't need to duplicate files to save different versions in an intransparent way. It also gives us the ability to easily revert to previous versions of files and makes collaboration easier, allowing changes by multiple people to be merged into a common repository.

**Documentation**: [https://git-scm.com/doc](https://git-scm.com/doc)

#### 1.2.3.1 Register a GitHub Account

- If you don't yet have a GitHub account, sign up [here](https://github.com/).

#### 1.2.3.2 Install Git in WSL

**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-git](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-git)

- Run the following from your bash command line interface (inside Windows Terminal) to install the latest stable Git version:
```sudo apt-get install git```.

#### 1.2.3.3 Git Config File Setup

- To set up the Git config file, run:
```git config --global user.name "<YOUR_NAME>"``` and replace <YOUR_NAME> with your Github Account user name.
- Then run ```git config --global user.email "<YOUR_EMAIL>"``` and replace <YOUR_EMAIL> with your Github Account email.
- If you need to edit the Git config, you can use the text editor nano as follows:
```nano ~/.gitconfig```. When you are done, save the changes with CTRL + X  -> Y -> Enter.

#### 1.2.3.4 Using Git

- From the bash command line interface in your Windows Terminal, run: ```git clone https://github.com/sebastianbirk/datascience-bootcamp.git```. This will create a local version of this repository in your WSL. This is needed before we can progress with subsequent steps. 
- Type ```ls``` to list all files and directories and you should now see a new folder called "datascience-bootcamp".
- To update your local repository to the must up-to-date status of the remote version, navigate into your repository (```cd datascience-bootcamp```; **Note:** you can use the tap key to autocomplete the directory name) and type ```git pull```. We will run this command at the start of every session of the bootcamp to have the up-to-date content.
- Udacity has a very good free course about Git essentials [here](https://www.udacity.com/course/version-control-with-git--ud123), which we can recommend. In general, we would strongly advise to use Git for version control for your future coding projects. For Avanade internal projects we can also use Git with Azure DevOps (Azure Repos) instead of Github. Find more information on using Git with Azure DevOps [here](https://docs.microsoft.com/en-us/azure/devops/user-guide/code-with-git?view=azure-devops).

### 1.2.4 Miniconda & Python

Miniconda is a small bootstrap version of Anaconda that includes only conda, Python and the packages they depend on as well as a small number of other useful packages including pip, zlib and few others. Anaconda is the world’s most popular open-source Python distribution platform and one of its main components, conda, is an open-source package and environment management system that runs on Windows, macOS, and Linux. With conda, we can quickly install, run, and update packages and their dependencies. It allows us to easily create, save, load, and switch between environments on our local computer, thus enabling an isolated, project-specific environment management. Conda was initially created for Python programs, but it can package and distribute software for any language. 

**Documentation**: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

#### 1.2.4.1 Install Miniconda with Python 3.9 in WSL

**Documentation & Instructions**: [https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

- In the bash command line interface in the Windows Terminal (WSL Ubuntu profile), run the following to download the Miniconda installation script: ```wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh```
- Then, run the script to install Miniconda: ```bash Miniconda3-py39_4.12.0-Linux-x86_64.sh``` and follow the prompts on the installer screens. Answer "yes" to all questions, particularly to whether you wish the installer to initialize Miniconda3 by running conda init.
- Afterwards, you can remove the installation script: ```rm Miniconda3-py39_4.12.0-Linux-x86_64.sh```.
- To make the installation changes take effect, close and then re-open your terminal window.
- Run ```conda list``` to verify that conda is now installed. If an output of packages is returned, you are good to go; otherwise it will tell you that the conda command was not found.

#### 1.2.4.2 Create the Conda Environment

We will now create our first conda environment to install all required packages for the bootcamp. The most reproducible and recommended way to install a conda environment is from an environment definition in a ".yml" file. To this end, the repository that we just cloned in the previous step contains an "environment.yml" file where the Python version as well as all required packages including their respective versions are defined. We can install the conda environment from the "environment.yml" file as follows:
- First navigate to the root of your local repository by running ```cd datascience-bootcamp```.  
- Then run ```conda env create -f environment.yml``` to install the conda environment defined in the "environment.yml" file. **Note**: When using WSL, it can happen that Conda fails to connect to the anaconda repo and returns a CondaHTTPError. If that is the case, open the Windows Command Prompt and type ```wsl --shutdown```. This will restart WSL. Then open WSL and try again.
- After the installation is done, run ```conda env list``` to list all conda environments. Next to the "base" environment, which is installed by default, you should now see the environment named "datascience-bootcamp".
- You can activate the new environment by running ```conda activate datascience-bootcamp```. We will activate this environment at the beginning of every session of the data science bootcamp. In your day-to-day work, we recommend to create different conda environments for different projects so that you have isolated environments and don't break things because of incompatability of packages across projects.
- To deactivate the new environment, run ```conda deactivate datascience-bootcamp```.
- OPTIONAL: to uninstall the newly installed conda environment, run ```conda env remove -n datascience-bootcamp```.

### 1.2.5 Azure CLI 

The Azure Command-Line Interface (CLI) is a cross-platform command-line tool to connect to Azure and execute administrative commands on Azure resources. It allows the execution of commands through a terminal using interactive command-line prompts or a script.

**Documentation**: [https://docs.microsoft.com/en-us/cli/azure/what-is-azure-cli](https://docs.microsoft.com/en-us/cli/azure/what-is-azure-cli)

#### 1.2.5.1 Install Azure CLI

**Documentation & Instructions**: [https://docs.microsoft.com/de-de/cli/azure/install-azure-cli](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)

- Run ```curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash``` to install the Azure CLI.

#### 1.2.5.2 Install Azure CLI Azure ML Extension

- Run ```az extension add -n azure-cli-ml``` to install the Azure CLI Azure ML Extension.

### 1.2.6 Terraform

Terraform is an open-source infrastructure as code software tool that enables you to safely and predictably create, change, and improve infrastructure.

**Documentation**: [https://www.terraform.io/](https://www.terraform.io/)

#### 1.2.6.1 Install Terraform

**Documentation & Instructions**: [https://learn.hashicorp.com/tutorials/terraform/install-cli](https://learn.hashicorp.com/tutorials/terraform/install-cli)

- Run ```sudo apt-get update && sudo apt-get install -y gnupg software-properties-common``` to ensure that your system is up to date, and you have the gnupg, software-properties-common, and curl packages installed. You will use these packages to verify HashiCorp's GPG signature, and install HashiCorp's Debian package repository.
- Run ```wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor | sudo tee /usr/share/keyrings/hashicorp-archive-keyring.gpg``` to install the HashiCorp GPG key.
- Run ```gpg --no-default-keyring --keyring /usr/share/keyrings/hashicorp-archive-keyring.gpg --fingerprint``` to verify the key's fingerprint.
- Run ```echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list``` to add the official HashiCorp repository to your system.
- Run ```sudo apt update``` to download the package information from HashiCorp.
- Run ```sudo apt-get install terraform``` to install Terraform from the new repository.

### 1.2.7 Docker

Docker is a software platform that allows you to build, test, and deploy applications quickly. Docker packages software into standardized units called containers that have everything the software needs to run including libraries, system tools, code, and runtime.

**Documentation**: [https://docs.docker.com/](https://docs.docker.com/)

#### 1.2.7.1 Install Docker

**Documentation & Instructions**: [https://medium.com/geekculture/run-docker-in-windows-10-11-wsl-without-docker-desktop-a2a7eb90556d](https://medium.com/geekculture/run-docker-in-windows-10-11-wsl-without-docker-desktop-a2a7eb90556d)

- Run ```sudo apt update``` to updated the local repository.
- Run ```sudo apt install docker.io -y``` to install Docker.
- Run ```docker --version``` to check the Docker installation.
- Enable automatic start of Docker Daemon on WSL:
    - Modify /etc/sudousers file, which controls how sudo command are executed. We need to make the following modifications to start dockerd without being prompted for a password every time you start a terminal window. Run ```sudo visudo``` and add the following to the bottom of the file: 
        - ```
          # Docker daemon specification
          <USERNAME> ALL=(ALL) NOPASSWD: /usr/bin/dockerd
          ``` 
          (Please replace `<USERNAME>` with your username).
    - Open the .bashrc file by running ```nano ~/.bashrc```. Then add the following to the bottom of the file:
         -  ```
            # Start Docker daemon automatically when logging in if not running.
            RUNNING=`ps aux | grep dockerd | grep -v grep`
            if [ -z "$RUNNING" ]; then
                sudo dockerd > /dev/null 2>&1 &
                disown
            fi
            ```
    - Add your username to docker group so you can run docker as a non-root user by running ```sudo usermod -aG docker <USERNAME>```. Again, replace `<USERNAME>` with your username.
- Validate the Docker installation by running ```docker run hello-world```.

### 1.2.8 Visual Studio Code (VSCode)

Visual Studio Code, commonly referred to as VSCode, is a lightweight but powerful source code editor which runs on your desktop and is available for Windows, macOS and Linux. It comes with support for many languages including Python and has a rich ecosystem of useful extensions, e.g. for working with Git and Azure including a source control tab that will show your changes and handle a variety of git commands for you.. With VSCode we can take advantage of features like Intellisense code completion, linting, debug support, code snippets, and unit testing. Learn more about VS Code's Git support here:
https://code.visualstudio.com/docs/editor/versioncontrol#_git-support

**Documentation**: [https://code.visualstudio.com/docs](https://code.visualstudio.com/docs)

#### 1.2.8.1 Install VSCode

**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode](https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-vscode)

- Visit the [VS Code install page](https://code.visualstudio.com/download) and download the installer for Windows. Then install Visual Studio Code on Windows (not in your WSL file system).
- When prompted to Select Additional Tasks during installation, be sure to check the Add to PATH option so you can easily open a folder in WSL using the code command.

#### 1.2.8.2 Install VSCode Remote Development Extension

- Install the [Remote Development extension pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack). This extension pack includes the Remote - WSL extension, in addition to the Remote - SSH, and Remote - Containers extensions, enabling you to open any folder in a container, on a remote machine, or in WSL.

#### 1.2.8.3 Open a WSL project in Visual Studio Code

- Open your Linux distribution's command line via Windows Terminal and type ```code .``` (**Note:** it might take some time to install the VS Code Server if you run the command for the first time).
- You can also access more VS Code Remote options by using the shortcut: CTRL+SHIFT+P in VS Code to bring up the command palette. If you then type Remote-WSL you will see a list of the VS Code Remote options available, allowing you to reopen the folder in a remote session, specify which distribution you want to open in, and more.

#### 1.2.8.4 Extensions inside of VS Code Remote

- The Remote-WSL extension splits VS Code into a “client-server” architecture, with the client (the user interface) running on your Windows machine and the server (your code, Git, plugins, etc) running remotely in WSL.
- When running VS Code Remote, extensions can therefore be installed either on your local machine or in your WSL distribution (remote). Selecting the 'Extensions' tab will display a list of extensions split between your local machine and your WSL distribution. Extensions for the client (the user interface), like themes, are installed once on your local machine. Installing server extensions on the remote, like the Python extension, or anything that handles things like linting or debugging, must be done separately in your WSL distribution (once in each one if you have multiple). VS Code will display a warning icon ⚠, along with a green "Install in WSL" button, if you have an extension locally installed that is not installed in your WSL.
- Now install the [Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) in your WSL distribution.

### 1.2.9 JupyterLab

JupyterLab is the latest open-source web-based interactive development environment for notebooks, code, and data. As such, it is one of the most popular tools for Data Scientists. Its flexible interface allows users to configure and arrange workflows in data science, scientific computing, computational journalism, and machine learning. A modular design invites extensions to expand and enrich functionality.

**Documentation**: [https://jupyterlab.readthedocs.io/en/stable/](https://jupyterlab.readthedocs.io/en/stable/)

#### 1.2.9.1 Run JupyterLab 

- Activate the datascience-bootcamp conda environment by opening your Linux distribution's command line via Windows Terminal and typing ```conda activate datascience-bootcamp```.
- Then type ```jupyter lab --no-browser``` to launch JupyterLab. Copy the URL, open the browser of your choice on your local workstation (e.g. Google Chrome), and paste the URL into the address bar. (**Note**: don't close the terminal as we have started an interactive JupyterLab session, which will be terminated once you close your terminal. You can stop the interactive session by pressing "CTRL + C".)
- You can now work with notebooks (".ipynb" format) in JupyterLab and follow the hands-on lab sessions during the rest of the data science bootcamp. All packages that you will need during the bootcamp are defined in the "environment.yml" file and have therefore been installed in your conda environment called "datascience-bootcamp". Since we started the JupyterLab session from within this environment, you have now access to all required packages.

## 1.3 Introduction to Python

- Now that we have started a JupyterLab session, open the notebook **"1.3_python_introduction"** in the **"01_bootcamp_intro_tools_setup_&_python_intro"** folder from your JupyterLab browser application. Then, go through the notebook by following the instructions written directly in the markdown cells of this notebook.

## 1.4 Summary Remarks

Congratulations on making it until here! You have learned a great deal about different useful data science tools that can be leveraged to efficiently run analyses with your data and you have installed these tools on your local workstation so that you can use them for this bootcamp and your future projects. In addition, you have taken your first steps to learn Python, one of the most powerful general-purpose programming languages and the leading programming language among data scientists. From here on, we will deep dive into different data-related topics, many of which will have lab sessions in notebooks similar to as you have seen in the "1.3_python_introduction" notebook. Thanks to our conda environment, you will have all required Python packages to your availability and the only thing you have to worry about is activating the environment and running JupyterLab from within the environment.
