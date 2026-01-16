terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  zone = "ru-central1-a" # https://yandex.cloud/ru/docs/overview/concepts/geo-scope
}

variable "run" {
  type = string
}

resource "yandex_compute_disk" "boot-disk-1" {
  name     = "boot-d-${var.run}"
  type     = "network-hdd"
  zone     = "ru-central1-a"
  size     = "20"
  image_id = "fd84mnbiarffhtfrhnog" # yc compute image list --folder-id standard-images --format json | jq -r '.[] | select(.name == "ubuntu-24-04-lts-v20251006") | .id'
}

resource "yandex_compute_instance" "vm-1" {
  name = "vm-wh-devops-${var.run}"

  resources {
    cores  = 2
    memory = 2
  }

  boot_disk {
    disk_id = yandex_compute_disk.boot-disk-1.id
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat       = true
  }

  metadata = {
    ssh-keys = "ubuntu:${file("../../check-assignment-github-key.pub")}"
  }
}

# resource "yandex_vpc_network" "network" {
# }

resource "yandex_vpc_subnet" "subnet" {
  name           = "network-ru-central1-a"
  zone           = "ru-central1-a"
  network_id     = "enpmkum36rqjr4ou5844"
  v4_cidr_blocks = ["10.128.0.0/24"]

  lifecycle {
    ignore_changes  = all
    prevent_destroy = true
  }
}

import {
  to = yandex_vpc_subnet.subnet
  id = "e9bu87fv0hqm13abdb7q"
}


# resource "yandex_vpc_network" "network-1" {
#   name = "network-wh-devops-${var.run}"
# }
#
# resource "yandex_vpc_subnet" "subnet-1" {
#   name           = "subnet-wh-devops-${var.run}"
#   zone           = "ru-central1-a"
#   network_id     = yandex_vpc_network.network-1.id
#   v4_cidr_blocks = ["192.168.10.0/24"]
# }

output "internal_ip_address_vm" {
  value = yandex_compute_instance.vm-1.network_interface.0.ip_address
}

output "external_ip_address_vm" {
  value = yandex_compute_instance.vm-1.network_interface.0.nat_ip_address
}
