output "s3_bucket_name" {
  description = "Name of the learning S3 bucket"
  value       = aws_s3_bucket.learning.id
}

output "s3_bucket_arn" {
  description = "ARN of the learning S3 bucket"
  value       = aws_s3_bucket.learning.arn
}

output "vpc_id" {
  description = "ID of the Caro VPC"
  value       = aws_vpc.caro.id
}

output "public_subnet_id" {
  value = aws_subnet.public.id
}

output "private_subnet_id" {
  value = aws_subnet.private.id
}

output "availability_zone" {
  value = data.aws_availability_zones.available.names[0]
}

output "internet_gateway_id" {
  value = aws_internet_gateway.caro.id
}

output "public_route_table_id" {
  value = aws_route_table.public.id
}

output "private_route_table_id" {
  value = aws_route_table.private.id
}

output "web_security_group_id" {
  value = aws_security_group.web.id
}

output "api_security_group_id" {
  value = aws_security_group.api.id
}

output "amazon_linux_ami_id" {
  description = "Latest Amazon Linux 2023 x86_64 AMI ID"
  value       = data.aws_ami.amazon_linux.id
}

output "amazon_linux_ami_name" {
  description = "Name of the selected Amazon Linux AMI"
  value       = data.aws_ami.amazon_linux.name
}

output "web_instance_id" {
  value = aws_instance.web.id
}

output "web_public_ip" {
  description = "Stable Elastic IP for the Caro web server"
  value       = aws_eip.web.public_ip
}

output "web_public_dns" {
  value = aws_instance.web.public_dns
}

