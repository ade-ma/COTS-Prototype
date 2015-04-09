Repo for the WeMo solution -- branch for the droplet server.

To run make sure flask and flask-cors are installed

    sudo pip install -U flask-cors

To set up the server, install uwsgi by running

    pip install uwsgi
    
Then run

    uwsgi --http ip-addres:5000 --wsgi-file server.py --callable app
    
NOTE: you need to run this commnd from the same folder as server.py.  Also, the listening server runs on port 5000, that is important so the raspi knows where to ping.
