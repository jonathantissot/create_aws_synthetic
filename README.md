# Project Details

This repository will hold the scripts needed to create a CloudWatch Canary.

## Pre-Requisites

To facilitate the execution of this script, you can run this using [Docker-Compose](https://docs.docker.com/compose/).

If you do not have Docker-Compose and Docker in your computer, you can install [Docker Desktop](https://www.docker.com/products/docker-desktop)


## Execution
This script will require you to pass a values.yaml. You can take the values_example.yaml and make a copy replacing the contents of it accordingly.

I went through the values_example.yaml adding comments to the line to explain what is required and what is not.

It will require you to provide a path for a folder to be zipped and uploaded to create the Canary. This folder can either be an absolute path or a relative path. This has been provided as an example script within the nodejs folder.

After you are set up, you can run:
```bash
docker-compose up
```

## Perks
* This script will create a role with the basic requirements for a Canary to work. You can add more from the `values.yaml` file.
* This script will add a UID to every name that is being created [such as Policies or Roles], except for the name of the Canary.

## Limitations
* This project will always upload files as Zip to create the Canary. I have not worked yet in using the data directly from S3.
* There is a wait time of 15 seconds between role creation, and the Canary setup as the Canary requires the role to be fully ready before proceeding.
* This project does not have test cases, they could be added in the future, but it is not a priority.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)