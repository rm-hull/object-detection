# object-detection

## Prerequisites

First you need to install some packages in the host system. Ensure you have a working Docker and docker-compose.

Inevitably the instructions at [Get started with the M.2 or Mini PCIe Accelerator](https://coral.ai/docs/m2/get-started/) are slightly
out of date. Below follows the updated instructions.

1. First, add our Debian package repository to your system (be sure you have an internet connection):
```
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list

sudo curl https://packages.cloud.google.com/apt/doc/apt-key.gpg > /etc/apt/trust.gpg.d/google-cloud.gpg

sudo apt-get update
```

2. Then install the PCIe driver and Edge TPU runtime packages:
```
sudo apt-get install gasket-dkms libedgetpu1-std
```

3. If the user account you'll be using does not have root permissions, you might need to also add the following udev rule, and then verify that the "apex" group exists and that your user is added to it:
```
sudo sh -c "echo 'SUBSYSTEM==\"apex\", MODE=\"0660\", GROUP=\"apex\"' >> /etc/udev/rules.d/65-apex.rules"

sudo groupadd apex

sudo adduser $USER apex
```

4. Reboot, and thats it.


## References

* https://coral.ai/docs/m2/get-started/
* https://github.com/gnometsunami/coral-container
* https://www.jeffgeerling.com/blog/2023/testing-coral-tpu-accelerator-m2-or-pcie-docker