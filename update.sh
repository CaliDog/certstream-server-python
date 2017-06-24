gsutil -m cp -a public-read -r html/_site/* gs://certstream-assets/
git push heroku master
