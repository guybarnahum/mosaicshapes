
# ...................................................................... lambad

# sky replacement lambda >> png mask
# bW lmabda
# mosaic lambda
# multi-res lambda
# multi-crop lambda
# cdn push lambda
# print lambda
# vectorize lambda
# scale up lambda
# pdf form + signature lambda

# Create local lambdas from var.lambdas for iteration

locals {
  lambdas = { for id, l in var.lambdas : id => l }
}

data "archive_file" "lambda_source_code" {
  for_each = local.lambdas
    type        = "zip"
    source_dir  = each.value.src_dir
    #source_file = each.value.src
    output_path = "${each.value.name}.zip"
}

# Layers
#data "klayers_package_latest_version" "Pillow" {
#  name   = "Pillow"
#  region = "us-west-2"
#}

resource "aws_lambda_function" "lambda_function" {
  for_each = local.lambdas

    function_name = each.key
    filename      = data.archive_file.lambda_source_code[each.key].output_path

    role          = aws_iam_role.lambda_role.arn
    runtime       = var.lambda_runtime
    handler       = "${each.value.module}.lambda_handler"
    timeout       = var.lambda_timeout
    memory_size   = var.lambda_memory
    architectures = var.lambda_architectures
    tags          = each.value.tags
    depends_on    = [aws_cloudwatch_log_group.lambda_log_group]

    source_code_hash = data.archive_file.lambda_source_code[each.key].output_base64sha256

    environment {
	    variables = {
        CreatedBy = "Terraform"
      }
	  }

    layers = [ 
      "arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p38-Pillow:6",
      "arn:aws:lambda:us-west-2:770693421928:layer:Klayers-p38-numpy:11",
      "arn:aws:lambda:us-west-2:770693421928:layer:Klayers-python38-scipy:1"
    ]
}

# Create log groups for each lambda

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  for_each = local.lambdas
    name              = "/aws/lambda/${each.key}"
    retention_in_days = 7
    lifecycle {
      prevent_destroy = false
   }
}

resource "null_resource" "sam_metadata_aws_lambda_function" {
    for_each = local.lambdas
      triggers = {
        resource_name = "aws_lambda_function.lambda_function[\"${each.key}\"]"
        resource_type = "ZIP_LAMBDA_FUNCTION"
        original_source_code = data.archive_file.lambda_source_code[each.key].source_dir
        built_output_path    = data.archive_file.lambda_source_code[each.key].output_path
    }
}

# .......................................................................... s3

# filtering lambdas by s3 trigger event

locals {
 s3_lambdas = { 
    for id, l in var.lambdas : id => l if l.trigger == "s3_event" 
  }
}

# Creating s3 resource for invoking to lambda function

resource "aws_s3_bucket" "lambda_s3_bucket" {
  for_each = local.s3_lambdas
    #name = replace("{each.value.name}", "_", "-")
    #bucket = "$(replace({each.value.name}, '_', '-'))-bucket-us-west-2"
    bucket = "${each.value.name}-bucket-us-west-2"
    tags = each.value.tags
}

resource "aws_s3_object" "input_directory" {
  for_each = local.s3_lambdas
    bucket = "${aws_s3_bucket.lambda_s3_bucket[each.key].id}"
    acl     = "public-read-write"
    key     =  "input/"
    content_type = "application/x-directory"
}

resource "aws_s3_object" "output_directory" {
  for_each = local.s3_lambdas
    bucket = "${aws_s3_bucket.lambda_s3_bucket[each.key].id}"
    acl     = "public-read-write"
    key     =  "output/"
    content_type = "application/x-directory"
}

resource "aws_s3_bucket_public_access_block" "lambda_s3_bucket" {
  for_each = local.s3_lambdas
    bucket = "${aws_s3_bucket.lambda_s3_bucket[each.key].id}"

    block_public_acls   = false
    block_public_policy = false
    ignore_public_acls  = false
}

data "aws_iam_policy_document" "s3_allow_access_policy_document" {

  for_each = local.s3_lambdas
    statement {
      effect = "Allow"

      actions = [
       "s3:Get*",
       "s3:List*",
      ]
    
      resources = ["arn:aws:s3:::${each.value.name}-bucket-us-west-2/*"]

      sid = "PublicReadGetObject"
      principals {
        type        = "*"
        identifiers = ["*"]
      }
    }
}

resource "aws_s3_bucket_policy" "s3_allow_access_policy" {
  for_each = local.s3_lambdas
    bucket = "${aws_s3_bucket.lambda_s3_bucket[each.key].id}"
    policy = data.aws_iam_policy_document.s3_allow_access_policy_document["${each.key}"].json
}

# Adding S3 bucket as trigger to my lambda and giving the permissions

resource "aws_s3_bucket_notification" "aws-lambda-trigger" {
  for_each = local.s3_lambdas
    bucket = "${aws_s3_bucket.lambda_s3_bucket[each.key].id}"
    
    lambda_function {
      lambda_function_arn = "${aws_lambda_function.lambda_function[each.key].arn}"
      events              = ["s3:ObjectCreated:*"]
      #filter_prefix       = "file-prefix"
      #filter_suffix       = "jpg"
    }
}

resource "aws_lambda_permission" "lambda_s3_permission" {
  for_each = local.s3_lambdas
    statement_id  = "AllowS3Invoke"
    action        = "lambda:InvokeFunction"
    function_name = "${each.key}"
    principal = "s3.amazonaws.com"
    source_arn = "arn:aws:s3:::${aws_s3_bucket.lambda_s3_bucket[each.key].id}"
}

# .......................................................................... s3

# filtering lambdas by cloudwatch trigger event

locals {
  cw_lambdas = { 
    for id, l in var.lambdas : id => l if l.trigger == "cw_event" 
  }
}

resource "aws_cloudwatch_event_rule" "hourly_event_rule" {
  name                  = "run-lambda-function"
  description           = "Schedule lambda function"
  schedule_expression   = "rate(1 hour)"
  #is_enabled = lookup
}

resource "aws_lambda_permission" "allow_cloudwatch" {
  for_each = local.cw_lambdas
    statement_id = "AllowExecutionFromCloudWatch"
    action = "lambda:InvokeFunction"
    function_name = "${each.key}"
    principal = "events.amazonaws.com"
    source_arn = aws_cloudwatch_event_rule.hourly_event_rule.arn
}

resource "aws_cloudwatch_event_target" "lambda-function-target" {
  for_each = local.cw_lambdas
    target_id = "lambda-function-target"
    rule      = aws_cloudwatch_event_rule.hourly_event_rule.name
    arn       = aws_lambda_function.lambda_function[each.key].arn
}
