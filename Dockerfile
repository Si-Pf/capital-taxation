FROM heroku/miniconda

# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt

# Install dependencies
RUN pip install -qr /tmp/requirements.txt

# Add our code
ADD ./ /opt/
WORKDIR /opt/

RUN conda install -c gettsim gettsim 

CMD web: bokeh serve --port=$PORT --allow-websocket-origin=capital-taxation.herokuapp.com --address=0.0.0.0 --use-xheaders myapp