build-AwsLambdaFunctionLambdaFunctionHourlyEventAA8BBD52:
	python3 ".aws-sam-iacs/iacs_metadata/copy_terraform_built_artifacts.py" --expression "|values|root_module|resources|[?address==\"null_resource.sam_metadata_aws_lambda_function[\"hourly_event\"]\"]|values|triggers|built_output_path" --directory "$(ARTIFACTS_DIR)" --target "null_resource.sam_metadata_aws_lambda_function[\"hourly_event\"]"
build-AwsLambdaFunctionLambdaFunctionMosaicS375A2D2B4:
	python3 ".aws-sam-iacs/iacs_metadata/copy_terraform_built_artifacts.py" --expression "|values|root_module|resources|[?address==\"null_resource.sam_metadata_aws_lambda_function[\"mosaic_s3\"]\"]|values|triggers|built_output_path" --directory "$(ARTIFACTS_DIR)" --target "null_resource.sam_metadata_aws_lambda_function[\"mosaic_s3\"]"
