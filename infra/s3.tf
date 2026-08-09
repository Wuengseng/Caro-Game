resource "aws_s3_bucket" "learning" {
  bucket = local.bucket_name

  tags = {
    Name    = "caro-game-learning"
    Purpose = "learning-resource-lifecycle"
    Lesson  = "terraform-update"
  }

  lifecycle {
    prevent_destroy = true
  }
}
resource "aws_s3_bucket_public_access_block" "learning" {
  bucket = aws_s3_bucket.learning.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "learning" {
  bucket = aws_s3_bucket.learning.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "learning" {
  bucket = aws_s3_bucket.learning.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}