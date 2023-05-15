import re
import sys
import os
import pandas as pd


def writeOpenStack():
    with open('instances.tf', 'w') as f:
        f.write(' resource "openstack_compute_instance_v2" "openstack.cws" {\n'
                'name            = "basic"\n'
                'image_id        = "id"\n'
                'flavor_id       = "3"\n'
                'key_pair        = "sshkey"\n'
                'security_groups = ["default"]\n'
                'metadata = { this = "written by cws"}\n'
                'network {\n'
                'name = "netsys_net"\n'
                '}\n'
                '}')


def writeProxmox():

    content = '''
    
    # Define variables
variable "vm_name" {
  type    = string
  default = "proxmox_vm"
}

variable "ssh_public_key" {
  type    = string
  default = "ssh-rsa ...}

variable "node_name" {
  type    = string
  default = "pve"
}


variable "template_name" {
  type    = string
  default = "ubuntu-20.04-LTS"
}

variable "vm_memory" {
  type    = number
  default = 512
}

variable "vm_disk_size" {
  type    = number
  default = 10
}

# Create a Proxmox virtual machine
resource "proxmox_vm_qemu" "proxmox_vm" {
  name        = var.vm_name
  target_node = var.node_name
  clone    = var.template_name
  memory      = var.vm_memory
  cores		= 2
  agent = 1

  
  disk {
    size     = "10G"
    type     = "scsi"
    storage  = "poolname"
    iothread = 0
  }

    network {
    model  = "virtio"
    bridge = "vmbr0"
#    ipconfig0 = "dhcp"
    tag = 300
  }

  ciuser = "user"
  cipassword = "password"
  sshkeys = var.ssh_public_key

  provisioner "file" {
    source = "/home/user/cws/firstrun.sh"
    destination = "/home/user/firstrun.sh"
    connection {
      type        = "ssh"
      user        = "user"
      private_key = file("/home/user/.ssh/id_rsa")
      host = self.ssh_host
    }
  }

    provisioner "file" {
      source = "/home/user/cws/agent.pp"
      destination = "/home/user/agent.pp"
          connection {
      type        = "ssh"
      user        = "user"
      private_key = file("/home/user/.ssh/id_rsa")
      host = self.ssh_host
    }
    }

    # Execute some shell commands on the VM
    provisioner "remote-exec" {
      connection {
      type        = "ssh"
      user        = "user"
      private_key = file("/home/user/.ssh/id_rsa")
      host = self.ssh_host
    }
      inline = [
        "sudo chmod +x firstrun.sh",
        "sudo bash firstrun.sh"
      ]
    }
  
}

    
    '''
    with open('tf/proxmox.tf', 'w') as f:
        f.write(content)



def writeGoogle():
    content = '''
    variable "project_id" {
    type = string
    default = "id"
    }

    provider "google" {
      project = var.project_id
      region  = "europe-north1"
    }

    resource "google_compute_network" "vpc_network" {
      name                    = "cws-vpc-network"
      auto_create_subnetworks = true
    }

    resource "google_compute_subnetwork" "vpc_subnet" {
      name          = "my-vpc-subnet"
      region        = "europe-north1"
      ip_cidr_range = "172.16.0.0/24"
      network       = google_compute_network.vpc_network.self_link
    }

    resource "google_compute_instance" "vm_instance" {
      name         = "my-vm"
      machine_type = "e2-medium"
      zone         = "europe-north1-a"

      boot_disk {
        initialize_params {
          image = "ubuntu-os-cloud/ubuntu-2004-lts"
        }
      }

      network_interface {
        network = google_compute_network.vpc_network.name
        access_config {}
      }
        metadata = {
        ssh-keys = "user:${file("/home/user/.ssh/id_rsa.pub")}"
      }
    }

    resource "google_compute_firewall" "nfs_firewall" {
      name    = "nfs-firewall"
      project = var.project_id
      network = google_compute_network.vpc_network.self_link

      allow {
        protocol = "tcp"
        ports    = ["2049"]
      }

      source_ranges = ["IP/32"]
    }

    resource "google_compute_firewall" "puppet_firewall" {
      name    = "puppet-firewall"
      project = var.project_id
      network = google_compute_network.vpc_network.self_link

      allow {
        protocol = "tcp"
        ports    = ["8140"]
      }

      source_ranges = ["IP/32"]
    }

    resource "google_compute_firewall" "wireguard_firewall" {
      name    = "wireguard-firewall"
      project = var.project_id
      network = google_compute_network.vpc_network.self_link

      allow {
        protocol = "udp"
        ports    = ["51821"]
      }

      source_ranges = ["IP/32"]
    }

    resource "google_compute_firewall" "ssh_firewall" {
      name    = "ssh-firewall"
      project = var.project_id
      network = google_compute_network.vpc_network.self_link

      allow {
        protocol = "tcp"
        ports    = ["22"]
      }

      source_ranges = ["0.0.0.0/0"]
    }
    '''

    with open('tf/google.tf', 'w') as f:
        f.write(content)

