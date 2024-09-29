# Installing NVIDIA Container Toolkit for GPU Support 🖥️⚙️

To enable GPU support inside Docker containers, you need to install the NVIDIA Container Toolkit. Follow these steps to ensure your Docker environment is configured to use your GPU.

### Prerequisites
- An NVIDIA GPU
- Updated NVIDIA drivers compatible with your GPU
- Docker installed with the Compose plugin ([Installation guide](https://docs.docker.com/compose/install/))

## Step-by-step installation
1. Configure the production repository:
    ```bash
    curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
    ```

    optionally (not required for this project), configure the repository to use experimantal packages:
    ```bash
    sed -i -e '/experimental/ s/^#//g' /etc/apt/sources.list.d/nvidia-container-toolkit.list
    ```

1. Update the packages list from the repository:
    ```bash
    sudo apt-get update
    ```

1. Install the NVIDIA Container Toolkit packages:
    ```bash
    sudo apt-get install -y nvidia-container-toolkit
    ```

## Configuring docker
1. Configure the container runtime by using the `nvidia-ctk` command:
    ```bash
    sudo nvidia-ctk runtime configure --runtime=docker
    ```
    The `nvidia-ctk` command modifies the `/etc/docker/daemon.json` file on the host. The file is updated so that Docker can use the NVIDIA Container Runtime.

1. Restart the Docker daemon:
    ```bash
    sudo systemctl restart docker
    ```

## Using NVIDIA GPUs in Docker Compose
Once the NVIDIA Container Toolkit is installed, you can use GPUs in your Docker Compose files by adding the following option to the service using the GPU:
```yaml
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1 # or how many you have
              capabilities: [gpu]
```
>[!INFO] 
> This is the default configuration used in `gpu-docker-compose.yml`

## Additional Resources
- [Installing the NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
- [Overview of installing Docker Compose](https://docs.docker.com/compose/install/)
