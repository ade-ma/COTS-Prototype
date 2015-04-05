Repo for the WeMo solution.

To run make sure flask and flask-cors are installed

    sudo pip install -U flask-cors

To set up the server, install uwsgi by running

    sudo apt-get install uwsgi
    sudo apt-get install uwsgi-plugin-python
    
Then run

    uwsgi --http ip-addres:port --plugin python --wsgi-file server.py --callable app
    
NOTE: you need to run this commnd from the same folder as server.py
