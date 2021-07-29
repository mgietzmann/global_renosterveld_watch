export TEMPLATE_IMAGE="gcr.io/ee-vegetation-gee4geo/dataflow/grw_recombine:latest"
export TEMPLATE_PATH="gs://grw-recombine/dataflow/templates/grw_recombine.json"
gcloud builds submit --tag "$TEMPLATE_IMAGE" .
gcloud dataflow flex-template build $TEMPLATE_PATH \
  --image "$TEMPLATE_IMAGE" \
  --sdk-language "PYTHON" \
  --metadata-file "metadata.json"
