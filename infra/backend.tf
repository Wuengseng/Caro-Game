terraform {
  backend "s3" {
    bucket       = "caro-game-learning-727165267644"
    key          = "terraform-state/caro-game.tfstate"
    region       = "ap-southeast-1"
    profile      = "caro-terraform-s3-process"
    encrypt      = true
    use_lockfile = true
  }
}