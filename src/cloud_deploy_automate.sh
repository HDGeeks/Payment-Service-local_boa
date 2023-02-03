#!/bin/bash

gcloud config set account daniel.tesfai@kinideas.com
gcloud config set project kin-project-352614

gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  compute.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  artifactregistry.googleapis.com

PROJECT_ID=$(gcloud config get-value core/project)
REGION=europe-west1

gcloud iam service-accounts create payment-service-account

SERVICE_ACCOUNT=$(gcloud iam service-accounts list \
    --filter payment-service-account --format "value(email)")

# gcloud sql instances create kinmusic-postgresql-v14 \
#   --project $PROJECT_ID \
#   --database-version POSTGRES_14 \
#   --cpu=2 \
#   --memory=7680MB \
#   --no-assign-ip \
#   --region $REGION \
#   --storage-auto-increase \


gcloud sql databases create kinpayment-cloudrun-database --instance kinmusic-postgresql-v14

kinpayment_cloudrun_database_admin_password="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"
gcloud sql users create kinpayment_cloudrun_database_admin --instance kinmusic-postgresql-v14 --password $kinpayment_cloudrun_database_admin_password

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:${SERVICE_ACCOUNT} \
    --role roles/cloudsql.client

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member serviceAccount:${SERVICE_ACCOUNT} \
    --role roles/storage.admin

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
     --member serviceAccount:${SERVICE_ACCOUNT} \
     --role roles/secretmanager.secretAccessor

GS_BUCKET_NAME=${PROJECT_ID}-kinmusic-storage
# gsutil mb -l ${REGION} gs://${GS_BUCKET_NAME}

echo DATABASE_URL=\"postgres://kinpayment_cloudrun_database_admin:${kinpayment_cloudrun_database_admin_password}@//cloudsql/${PROJECT_ID}:${REGION}:kinmusic-postgresql-v14/kinpayment-cloudrun-database\" > .env
echo GS_BUCKET_NAME=\"${GS_BUCKET_NAME}\" >> .env
echo SECRET_KEY=\"$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 50 | head -n 1)\" >> .env
echo DEBUG=\"True\" >> .env

gcloud secrets create payment_service_settings --data-file .env

gcloud secrets add-iam-policy-binding payment_service_settings \
  --member serviceAccount:${SERVICE_ACCOUNT} \
  --role roles/secretmanager.secretAccessor
rm .env

export PROJECTNUM=$(gcloud projects describe ${PROJECT_ID} --format 'value(projectNumber)')
export CLOUDBUILD=${PROJECTNUM}@cloudbuild.gserviceaccount.com

gcloud secrets add-iam-policy-binding payment_service_settings \
  --member serviceAccount:${CLOUDBUILD} \
  --role roles/secretmanager.secretAccessor

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:${CLOUDBUILD} \
    --role roles/cloudsql.client

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:${CLOUDBUILD} \
    --role roles/storage.admin

payment_admin_password="$(cat /dev/urandom | LC_ALL=C tr -dc 'a-zA-Z0-9' | fold -w 30 | head -n 1)"

echo -n "${payment_admin_password}" | gcloud secrets create payment_admin_password --data-file=-

gcloud secrets add-iam-policy-binding payment_admin_password \
  --member serviceAccount:${CLOUDBUILD} \
  --role roles/secretmanager.secretAccessor

gcloud builds submit --region=${REGION} --pack image=eu.gcr.io/${PROJECT_ID}/payment_service_image

gcloud builds submit --region=${REGION} --config migrate.yaml --substitutions _REGION=$REGION

gcloud run deploy payment-service \
  --platform managed \
  --region $REGION \
  --image eu.gcr.io/${PROJECT_ID}/payment_service_image \
  --set-cloudsql-instances ${PROJECT_ID}:${REGION}:kinmusic-postgresql-v14 \
  --set-secrets PAYMENT_SERVICE_SETTINGS=payment_service_settings:latest \
  --service-account $SERVICE_ACCOUNT \
  --allow-unauthenticated

PAYMENT_SERVICE_URL=https://payment-service-vdzflryflq-ew.a.run.app

gcloud secrets versions access latest --secret payment_service_settings > temp_settings
echo PAYMENT_SERVICE_URL=${PAYMENT_SERVICE_URL} >> temp_settings
gcloud secrets versions add payment_service_settings --data-file temp_settings
rm temp_settings

gcloud run services update payment-service \
  --platform managed \
  --region $REGION \
  --image eu.gcr.io/${PROJECT_ID}/payment_service_image

gcloud secrets versions access latest --secret payment_admin_password && echo ""