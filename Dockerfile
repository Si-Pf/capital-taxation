FROM heroku/miniconda



# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt



# Install dependencies
RUN pip install -qr /tmp/requirements.txt

RUN conda install -c gettsim gettsim

# Add our code
ADD ./ /opt/
WORKDIR /opt/

CMD gunicorn --bind 0.0.0.0:$PORT wsgi