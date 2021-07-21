export REGION="us-central1"
export TEMPLATE_PATH="gs://grw-predict/dataflow/templates/grw_predict.json"

# Run the Flex Template. Note that GRW_PREDICT_INPUT and GRW_PREDICT_OUTPUT need to be set appropriately
gcloud dataflow flex-template run "grw-predict-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location "$TEMPLATE_PATH" \
    --parameters input="$GRW_PREDICT_INPUT" \
    --parameters output="$GRW_PREDICT_OUTPUT" \
    --parameters max_num_workers=50 \
    --parameters worker_machine_type=n1-standard-2 \
    --region "$REGION"