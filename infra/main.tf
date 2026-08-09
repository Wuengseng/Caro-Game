data "aws_caller_identity" "current" {}

output "aws_identity" {
  value = {
    account_id = data.aws_caller_identity.current.account_id
    arn        = data.aws_caller_identity.current.arn
  }
}