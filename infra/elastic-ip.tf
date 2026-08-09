resource "aws_eip" "web" {
  domain = "vpc"

  depends_on = [
    aws_internet_gateway.caro
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-web"
  }
}

resource "aws_eip_association" "web" {
  allocation_id = aws_eip.web.id
  instance_id   = aws_instance.web.id
}