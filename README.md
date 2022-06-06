# Data Science Bootcamp

## Setup

### 1. Windows Subsystem for Linux (WSL)
WSL enables us to use a Linux distribution operating system with Linux tools on our Windows machines in a completely integrated manner (no need to dual-boot).
When we install a Linux distribution with WSL, we are installing a new file system, separated from the Windows NTFS C:\ drive.

#### 1.1 Install WSL
**Documentation & Instructions**: https://docs.microsoft.com/en-us/windows/wsl/install

#### 1.2 Set up a WSL development environment
**Documentation & Instructions**: https://docs.microsoft.com/en-us/windows/wsl/setup/environment#set-up-your-linux-username-and-password

We can open the new file system with the Windows explorer by entering the home directory and starting the explorer executable:
```cd ~```
```explorer.exe .```


### 2. Windows Terminal

#### 2.1 Install Windows Terminal from the Microsoft Store
**Documentation & Instructions**: https://docs.microsoft.com/en-us/windows/terminal/install

#### 2.2 Set up Windows Terminal
Configure "Ubuntu" as your Startup Default profile as described in https://docs.microsoft.com/en-us/windows/terminal/install#set-your-default-terminal-profile.

### 3. Git

Git enables us to version control our files and track changes so that we have a nicely structured recorded history and don't need to duplicate files to save different versions in an intransparent way. It also gives us the ability to easily revert to previous versions of files and makes collaboration easier, allowing changes by multiple people to be merged into a common repository.

#### 3.1 Register a GitHub Account
If you don't yet have a GitHub account, sign up here:
https://github.com/

#### 3.1 Install Git in WSL
**Documentation & Instructions**: https://docs.microsoft.com/en-us/windows/wsl/tutorials/wsl-git

Run the following to install the latest stable Git version:
```sudo apt-get install git```

#### 3.2 Git Config File Setup
To set up the Git config file, run:
```git config --global user.name "<YOUR_NAME>"```
```git config --global user.email "<YOUR_EMAIL>"```

If you need to edit the Git config, you can use the text editor nano:
```nano ~/.gitconfig```
When you are done, save the changes with
CTRL + X  -> Y -> Enter

### 4. Miniconda

#### 4.1 Install Miniconda with Python 3.9 in WSL
**Documentation & Instructions**: https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html

In the WSL Ubuntu profile run the following to download the installation script:
```wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh```

Then, run the script to install Miniconda:
```bash Miniconda3-py39_4.12.0-Linux-x86_64.sh```

Afterwards, you can remove the installation script:
```rm Miniconda3-py39_4.12.0-Linux-x86_64.sh```

#### 4.2 Create the Miniconda Environment

### 5. Visual Studio Code (VSCode)
#### 5.1 Install VSCode

#### 5.2 Install VSCode Remote Development Extension

Visual Studio Code comes with built-in support for Git, including a source control tab that will show your changes and handle a variety of git commands for you. Learn more about VS Code's Git support here:
https://code.visualstudio.com/docs/editor/versioncontrol#_git-support

### Data Science Virtual Machine (Ubuntu 20.04)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fsebastianbirk%2Fdatascience-bootcamp%2Fmain%2Finfrastructure%2Fvm%2Ftemplate.json)

**Note**: If you are interested in learning more about Azure Deployment Buttons, check this out: https://docs.microsoft.com/en-us/azure/azure-resource-manager/templates/deploy-to-azure-button

```sudo apt install azure-cli```



### 1. Clone this repository
```git clone https://github.com/sebastianbirk/datascience-bootcamp.git```
> This is an example template for Avanade OSS projects.

```
Add a short description of your project.
DELETE THIS COMMENT
```

[![Commitizen friendly](https://img.shields.io/badge/commitizen-friendly-brightgreen.svg)](http://commitizen.github.io/cz-cli/)
![GitHub issues](https://img.shields.io/github/issues/Avanade/avanade-template)
![GitHub](https://img.shields.io/github/license/Avanade/avanade-template)
![GitHub Repo stars](https://img.shields.io/github/stars/Avanade/avanade-template?style=social)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](https://avanade.github.io/code-of-conduct/)
[![Incubating InnerSource](https://img.shields.io/badge/Incubating-Ava--Maturity-%23FF5800?labelColor=yellow)](https://avanade.github.io/maturity-model/)

```
Update the repo URL addresses for the shield templates.
DELETE THIS COMMENT
```

## Overview
Describe the project in more detail. **This project is an example project, to be used when creating new Avanade Open Source projects.**

```
Add a description of your project, and a screenshot if possible.
DELETE THIS COMMENT
```


## Licensing
avanade-template is available under the [MIT Licence](./LICENCE).
```
Update the project name.
DELETE THIS COMMENT
```

## Solutions Referenced

- [Azure SQL Database ledger tables](https://docs.microsoft.com/en-us/azure/azure-sql/database/ledger-overview?WT.mc_id=AI-MVP-5004204)
- [Azure Confidential Ledger](https://docs.microsoft.com/en-gb/azure/confidential-ledger/?WT.mc_id=AI-MVP-5004204)


```
These are provided as examples. Include links to components you have used, or delete this section.
DELETE THIS COMMENT
```

## Documentation
The `docs` folder contains [more detailed documentation](./docs/start-here.md), along with setup instructions.

```
Add an optional installation or usage section, if the instructions are <3 lines
e.g.
### Installation

### Usage

DELETE THIS COMMENT
```

## Contact
Feel free to [raise an issue on GitHub](https://github.com/Avanade/avanade-template/issues), or see our [security disclosure](./SECURITY.md) policy.
```
Update the repo URL.
DELETE THIS COMMENT
```
## Contributing
Contributions are welcome. See information on [contributing](./CONTRIBUTING.md), as well as our [code of conduct](https://avanade.github.io/code-of-conduct/).

If you're happy to follow these guidelines, then check out the [getting started](./docs/start-here.md) guide.

```
Leave the code of conduct unchanged
DELETE THIS COMMENT
```

## Who is Avanade?

[Avanade](https://www.avanade.com) is the leading provider of innovative digital, cloud and advisory services, industry solutions and design-led experiences across the Microsoft ecosystem.
```
Leave the boilerplate unchanged
DELETE THIS COMMENT
```

```
If needed, review the Open Source site on the intranet for more information.

Full details at https://avanade.sharepoint.com/sites/opensource

DELETE THIS COMMENT
```
