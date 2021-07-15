export TEMPLATE_IMAGE="gcr.io/ee-vegetation-gee4geo/samples/dataflow/prep_for_predict_v1:latest"
gcloud builds submit --tag "$TEMPLATE_IMAGE" .
export TEMPLATE_PATH="gs://reno-ee-example/samples/dataflow/templates/streaming-beam.json"
gcloud dataflow flex-template build $TEMPLATE_PATH \
  --image "$TEMPLATE_IMAGE" \
  --sdk-language "PYTHON" \
  --metadata-file "metadata.json"
