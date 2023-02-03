#!/bin/bash

gcloud config set account daniel.tesfai@kinideas.com
gcloud config set project kin-project-352614

gcloud iam service-accounts delete payment-service-account@kin-project-352614.iam.gserviceaccount.com
gcloud sql databases delete kinpayment-cloudrun-database --instance kinmusic-postgresql-v14
gcloud sql users delete kinpayment_cloudrun_database_admin --instance kinmusic-postgresql-v14
gcloud secrets delete payment_service_settings
gcloud secrets delete payment_admin_password
gcloud run services delete payment-service
