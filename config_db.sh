sudo apt install postgresql postgresql-contrib -y
sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
sudo -u postgres createdb -O cloud tasks
sudo su - postgres
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/12/main/postgresql.conf
sudo echo host all all 192.168.0.0/20 trust >> /etc/postgresql/12/main/pg_hba.confcd /
exit
sudo ufw allow 5432/tcp
sudo systemctl restart postgresql