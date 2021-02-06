FROM heroku/miniconda:3



# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt



# Install dependencies
RUN pip install -qr /tmp/requirements.txt

RUN conda install -c gettsim gettsim


# Add our code
ADD ./ /opt/
WORKDIR /opt/

CMD bokeh serve --port=$PORT --allow-websocket-origin=tax-reform.herokuapp.com --address=0.0.0.0 --use-xheaders App