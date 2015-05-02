#!/bin/sh
git --work-tree=/var/www/mosaicme --git-dir=/var/repo/mosaicme.git checkout -f

# set python path
export PATH=$PATH:/var/www/mosaicme

# Install dependencies
if [ -f /var/www/mosaicme/requirements.txt ]; then
        sudo pip install -r /var/www/mosaicme/requirements.txt
fi

# Copy dotenv file
cp /var/www/mosaicme/example.env /var/www/mosaicme/.env

sed -i 's/{{s3_access_key}}/USERNAME/g' /var/www/mosaicme/.env
sed -i 's,{{s3_secret_key}},SECRET_KEY,g' /var/www/mosaicme/.env
sed -i 's/{{s3_host}}/HOST/g' /var/www/mosaicme/.env
sed -i 's/{{s3_port}}/PORT/g' /var/www/mosaicme/.env
sed -i 's/{{s3_https}}/HTTPS/g' /var/www/mosaicme/.env

# Collect static files
python /var/www/mosaicme/mosaicme/web/manage.py collectstatic --noinput

# Restart Supervisor
sudo service supervisor restarT