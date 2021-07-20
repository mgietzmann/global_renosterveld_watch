export REGION="us-central1"
export TEMPLATE_PATH="gs://grw-preprocess/dataflow/templates/grw_preprocess.json"

# Run the Flex Template. Note that GRW_INPUT and GRW_OUTPUT need to be set appropriately
gcloud dataflow flex-template run "grw-preprocess-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location "$TEMPLATE_PATH" \
    --parameters input="$GRW_PREPROCESS_INPUT" \
    --parameters output="$GRW_PREPROCESS_OUTPUT" \
    --parameters max_num_workers=50 \
    --parameters worker_machine_type=n1-standard-2 \
    --region "$REGION"