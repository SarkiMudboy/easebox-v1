# Easebox

An dispatch ride hailing platform that helps businesses access last mile delivery services

## Develop locally

### Docker -

You can get the project locally by cloning into your local repo using
`git clone https://github.com/SarkiMudboy/easebox-v1.git`

Setup and install docker and docker desktop - see https://docs.docker.com/desktop/install/windows-install/

### Build image

In the project root, use the command
`docker compose --env-file=./easebox/.env up --build`
You can log the build progress to a file for debugging
`docker compose --env-file=./easebox/.env up --build > logs.txt`

### Spin up the container

Start the app using compose
`docker compose up`

Note: Ensure the environment variable file is in the project root
