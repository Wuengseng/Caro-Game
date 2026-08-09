variable "aws_region" {
  description = "AWS region dùng cho dự án"
  type        = string
  default     = "ap-southeast-1"
}

variable "project_name" {
  description = "Tên dự án"
  type        = string
  default     = "caro-game"
}

variable "environment" {
  description = "Tên môi trường"
  type        = string
  default     = "learning"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the Caro VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "IPv4 CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "private_subnet_cidr" {
  description = "IPv4 CIDR block for the private subnet"
  type        = string
  default     = "10.0.2.0/24"
}

variable "instance_type" {
  description = "EC2 instance type for the Caro learning server"
  type        = string
  default     = "t3.micro"

  validation {
    condition     = contains(["t3.micro", "t3.small"], var.instance_type)
    error_message = "Instance type must be t3.micro or t3.small for this learning environment."
  }
}