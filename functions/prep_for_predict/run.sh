export REGION="us-central1"
export TEMPLATE_PATH="gs://reno-ee-example/samples/dataflow/templates/streaming-beam.json"

# Run the Flex Template.
gcloud dataflow flex-template run "prep-for-predict-`date +%Y%m%d-%H%M%S`" \
    --template-file-gcs-location "$TEMPLATE_PATH" \
    --parameters input=gs://reno-ee-example/NEW_Image_reno_predict__2021-07-0800008.tfrecord.gz \
    --parameters output=gs://reno-ee-example/RealBeamOutput2 \
    --region "$REGION"