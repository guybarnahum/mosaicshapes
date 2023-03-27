
terraform {
  required_version = ">= 0.13.1"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 3.19"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 2.0"
    }
    klayers = {
      version = "~> 1.0.0"
      source  = "ldcorentin/klayer"
    }
  }
}

provider "aws" {
    region = "us-west-2" 
}

# ................................................................. credentials

data "aws_caller_identity" "current" {}

# ..................................................................... lambdas

variable "lambda_runtime" {}
variable "lambda_timeout" {}
variable "lambda_memory"  {}
variable "lambda_architectures" {}

variable "lambdas"{
  type = map(object({
    src_dir = string
    module  = string
    name    = string
    trigger = string
    tags    = map(string)
  }))

  default = {
    "hourly_event" = { 
      src_dir="artifacts/lambda-src/", 
      module="lambda",
      name="lambda-hourly-event", # lowercase + hyphens only
      trigger="cw_event", 
      tags={ Name = "Hourly Event", Environment = "Dev"}
    },
    "mosaic_s3" = { 
      src_dir="artifacts/mosaic-src/", #sym link! 
      #src_dir="../../mosaic/", 
      module="lambda",
      name="lambda-mosaic-s3",  # lowercase + hyphens only
      trigger="s3_event", 
      tags={ Name = "Mosaic S3", Environment = "Dev"}
    }
  }
}

# .......................................................................... s3


