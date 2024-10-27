sudo apt update -y
sudo apt upgrade -y  # Automatically upgrades packages without user interaction
sudo apt install -y nginx
sudo cp boilerplate/flask_app /etc/nginx/sites-enabled/flask_app
sudo cp boilerplate/.bash_profile ~/.bash_profile
sudo unlink /etc/nginx/sites-enabled/default
sudo nginx -s reload
sudo apt install -y python3
sudo apt install -y python3-pip
pip3 install -r requirements.txt
sudo apt install -y gunicorn3
sudo apt install -y tmux
pip install notebook
pip3 install jupyterlab
jupyter notebook --generate-config
sudo cp boilerplate/jupyter_notebook_config.py ~/.jupyter/jupyter_notebook_config.py
sudo cp boilerplate/jupyter_server_config.json ~/.jupyter/jupyter_server_config.json
sudo apt install -y postgresql postgresql-contrib
sudo -i -u postgres
createuser omni
createdb truthriver
psql -c "ALTER USER omni WITH PASSWORD 'planttheknowledgetree';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE truthriver TO omni;"
exit
sudo cp boilerplate/postgresql.conf /etc/postgresql/13/main/postgresql.conf
sudo cp boilerplate/pg_hba.conf /etc/postgresql/13/main/pg_hba.conf
sudo systemctl reload postgresql@13-main

source ~/.bash_profile
tmux new-session -s lab -d 'jupyter lab \
  --port=8080 \
  --NotebookApp.port_retries=0 \
  --allow-root'
tmux new-session -s prod -d "gunicorn3 --workers=3 --bind 0.0.0.0:8000 --timeout 60000 routes:app"
