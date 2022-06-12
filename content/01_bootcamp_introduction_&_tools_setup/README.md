# 1. Bootcamp Introduction & Tools Setup

## 1.1 Bootcamp Introduction

## 1.2 Tools Setup

### 1.2.1 Windows Subsystem for Linux (WSL)
WSL enables us to use a Linux distribution operating system with Linux tools on our Windows machines in a completely integrated manner (no need to dual-boot).
When we install a Linux distribution with WSL, we are installing a new file system, separated from the Windows NTFS C:\ drive.

#### 1.2.1.1 Install WSL
**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/install](https://docs.microsoft.com/en-us/windows/wsl/install)

- Open PowerShell or Windows Command Prompt in administrator mode and run
```wsl --install -d Ubuntu``` (this will install WSL together with an Ubuntu distribution, which is also the default; reboot may be required).
- Once you have installed WSL, open Ubuntu from the Windows start menu (if it has not opened automatically after installation). We can also pin Ubuntu to our Windows taskbar for easy accessibility in the future. 
- You will now be prompted to create a user account and password for your newly installed Linux distribution. This account will be considered the Linux administrator, with the ability to run sudo (Super User Do) administrative commands.
- We can now interact with our Ubuntu distribution through the bash console that was launched.

### 1.2.1.2 Set up a WSL development environment
**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/wsl/setup/environment#set-up-your-linux-username-and-password](https://docs.microsoft.com/en-us/windows/wsl/setup/environment)

- Upgrade your packages using the apt package manager by running ```sudo apt update && sudo apt upgrade``` in the launched bash console.
- We can open the new file system that comes with our Ubuntu distribution by leveraging the Windows explorer. To do this, enter the home directory and start the explorer executable from your Bash console as follows:
```cd ~```
```explorer.exe .```

### 1.2.2 Windows Terminal

#### 1.2.2.1 Install Windows Terminal from the Microsoft Store
**Documentation & Instructions**: [https://docs.microsoft.com/en-us/windows/terminal/install](https://docs.microsoft.com/en-us/windows/terminal/install)

- Install Windows Terminal from the Microsoft Store by following this link: [https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=de-de&gl=DE](https://apps.microsoft.com/store/detail/windows-terminal/9N0DX20HK701?hl=de-de&gl=DE).

#### 1.2.2.2 Set up Windows Terminal
- Configure "Ubuntu" as your Startup Default profile as described in [https://docs.microsoft.com/en-us/windows/terminal/install#set-your-default-terminal-profile](https://docs.microsoft.com/en-us/windows/terminal/install#set-your-default-terminal-profile).

### 1.2.3 Git

Git enables us to version control our files and track changes so that we have a nicely structured recorded history and don't need to duplicate files to save different versions in an intransparent way. It also gives us the ability to easily revert to previous versions of files and makes collaboration easier, allowing changes by multiple people to be merged into a common repository.

#### 1.2.3.1 Register a GitHub Account
If you don't yet have a GitHub account, sign up here:
https://github.com/

#### 1.2.3.2 Install Git in WSL
**Documentation & Instructions**: https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-git

Run the following to install the latest stable Git version:
```sudo apt-get install git```

#### 1.2.3.3 Git Config File Setup
To set up the Git config file, run:
```git config --global user.name "<YOUR_NAME>"```
```git config --global user.email "<YOUR_EMAIL>"```

If you need to edit the Git config, you can use the text editor nano:
```nano ~/.gitconfig```
When you are done, save the changes with
CTRL + X  -> Y -> Enter

### 1.2.4 Miniconda

#### 1.2.4.1 Install Miniconda with Python 3.9 in WSL
**Documentation & Instructions**: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html

In the WSL Ubuntu profile run the following to download the installation script:
```wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh```

Then, run the script to install Miniconda:
```bash Miniconda3-py39_4.12.0-Linux-x86_64.sh```

Afterwards, you can remove the installation script:
```rm Miniconda3-py39_4.12.0-Linux-x86_64.sh```

#### 1.2.4.2 Create the Miniconda Environment

### 1.2.5 Visual Studio Code (VSCode)
#### 1.2.5.1 Install VSCode

#### 1.2.5.2 Install VSCode Remote Development Extension

Visual Studio Code comes with built-in support for Git, including a source control tab that will show your changes and handle a variety of git commands for you. Learn more about VS Code's Git support here:
https://code.visualstudio.com/docs/editor/versioncontrol#_git-support

## Virtual Machine (Ubuntu 18.04)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsebastianbirk%2Fdatascience-bootcamp%2Fmain%2Finfrastructure%2Fvm%2Ftemplate.json)

Make sure to choose your own password before creating the resource and be aware that in a production scenario SSH keys would be the preferred authentication method and password should not be used.

**Note**: If you are interested in learning more about Azure Deployment Buttons, check this out: https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-to-azure-button

After your Virtual Machine is deployed, you can access it by opening the Command Prompt from your Windows machine and typing:
ssh server-admin@<DNS_NAME> where you can find the <DNS_NAME> on the Overview page of your Virtual Machine in the Azure Portal.

```sudo apt install azure-cli```
