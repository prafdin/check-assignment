# Docker image for run act locally

This image is only for local run act utility.
Image is based on origin act runner https://github.com/catthehacker/docker_images but with additional tools for running
integration tests for this repo.

# Build

## prafdin-ubuntu:hacked-act-latest
```bash
docker build -t prafdin-ubuntu:hacked-act-latest -f ubuntu-latest.Dockerfile .
```