#!/bin/bash

gcloud config set account daniel.tesfai@kinideas.com
gcloud config set project kin-project-352614

PROJECT_ID=$(gcloud config get-value core/project)
REGION=europe-west1

gcloud builds submit --region=${REGION} --pack image=eu.gcr.io/${PROJECT_ID}/payment_service_image

gcloud builds submit --region=${REGION} --config migrate.yaml --substitutions _REGION=$REGION

gcloud run services update payment-service \
  --platform managed \
  --region $REGION \
  --image eu.gcr.io/${PROJECT_ID}/payment_service_image