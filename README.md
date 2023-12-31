# Recursive-REST &middot; [![Inline docs](https://inch-ci.org/github/dwyl/hapi-auth-jwt2.svg?branch=master)](https://github.com/apexDev37/Recursive-REST/blob/main/README.md) [![Docker version](https://img.shields.io/badge/-v20.10.23-grey?style=flat&logo=docker)]() [![Python version](https://img.shields.io/badge/-v3.11.4-grey?style=flat&logo=python&logoColor=yellow)](https://www.python.org/downloads/) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](http://makeapullrequest.com) [![Activity](https://img.shields.io/badge/status-active-brightgreen)](https://github.com/apexDev37/Recursive-REST/commits/main)
> A simple devops-inspired template for Django applications setup with compose. 

## Introduction
Recursive-REST is a small application that exposes a REST endpoint and calls itself, _itself_ using OAuth 2.0. This repository is mostly for experimentation, exploring Django community tools, and testing the behavior of specific functionality of interest. Let's get _recursive_! Any comments, feedback, and contributions are highly appreciated.  I always love to hear and learn from the community❤ 

Learn more about the Django framework from the official [documentation].

## Installing / Getting started
This is an overview of the minimal setup needed to get started.

### Prerequisites
- [Git]
- [Docker]
- [Docker Compose]
- [Docker Desktop]
- IDE/Code/Text editor ([PHPStorm], [VScode], [Vim], etc)

Follow these tutorials on setting up Docker and Compose on either [Mac] or [Linux]. I'd recommend Microsoft's documentation to set up [Docker on WSL2] if you're on Windows. 

### Local Setup
> The following setup was run on Ubuntu focal (20.04.6 LTS)

You can clone this repo with the following command.

- Clone repository
``` bash
    # cd your/desired/target/dir
    $ git clone git@github.com:apexDev37/Recursive-REST.git
    $ cd my-project
```

> This will clone the repository to a target dir on your host machine with a custom name `my-project/` and navigate into its root dir.

### Configuration
Before running your application with Compose, configure your environment variables in the `./.envs/` directory. Example `env` files are provided to configure the following instances: Django and Postgres. You can create the required `env` files with the following code snippet.

- Create env files
``` bash
    # ensure you're in the project's root
    $ for file in .envs/*.example; do cp "$file" "${file%.example}"; done
    $ cd .envs/
```

> This will loop through all the files in the .envs/ directory that end with .example and creates new files without the `.example` extension (ie. `django.env.example` -> `django.env`).
 
NOTE: After the `env` files are created, replace the placeholders in the files with your own values specific to your Django application and Postgres container.

### Launch
You're all set to run your Django application. Spin up your Django and Postgres instances with the following command.

- Spin up containers
``` bash
    $ docker compose down
    $ docker compose up -d
```

> This will create and start the Django and Postgres instances in the same network defined in the `compose` file.

Once the containers have been created and started, you can access the application at http://localhost:8000
<img src="./resources/docs/images/successful-django-install.PNG" alt="Successful Django Install Page"/>


## Licensing
To make a repository open source, you must license it so that others may freely use, modify, and distribute the software. Using the [MIT license], this project ensures this. The full original text version of the license may be seen [here]. To apply the right to your repository, follow the procedures.



[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does
its job. There is no need to format nicely because it shouldn't be seen.
Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

<!-- Introduction links -->
[documentation]: <https://docs.djangoproject.com/en/>

<!-- Installing / Getting Started links -->
[Git]: <https://git-scm.com/>
[Docker]: <https://www.docker.com/>
[Docker Compose]: <https://docs.docker.com/compose/>
[Docker Desktop]: <https://www.docker.com/products/docker-desktop/>
[Mac]: <https://docs.docker.com/desktop/install/mac-install/>
[Linux]: <https://docs.docker.com/desktop/install/linux-install/>
[Docker on WSL2]: <https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-containers>

[PHPStorm]: <https://www.jetbrains.com/phpstorm/>
[VScode]: <https://code.visualstudio.com/>
[Vim]: <https://www.vim.org/>

<!-- Licensing links -->
[MIT license]: <https://en.wikipedia.org/wiki/MIT_License>
[here]: <https://choosealicense.com/licenses/mit/>