provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "spectra_guardian" {
  ami           = "ami-0c02fb55956c7d316"
  instance_type = "t2.medium"
  key_name      = var.key_name

  tags = {
    Name = "spectra_guardian_server"
  }

  provisioner "remote-exec" {
    inline = [
      "sudo apt update",
      "sudo apt install -y docker.io docker-compose",
      "sudo systemctl start docker",
      "sudo systemctl enable docker",
      "git clone https://github.com/yourgithubuser/spectra_guardian.git /home/ubuntu/spectra_guardian",
      "cd /home/ubuntu/spectra_guardian",
      "sudo docker-compose up --build -d"
    ]

    connection {
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(var.private_key_path)
      host        = self.public_ip
    }
  }
}

variable "key_name" {
  description = "Name of the AWS EC2 key pair"
}

variable "private_key_path" {
  description = "Path to private SSH key for EC2 access"
}
