grpc_schemas:
	python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/iracingsetups_client/*.proto