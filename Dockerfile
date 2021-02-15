FROM continuumio/miniconda3

# Grab requirements.txt.
ADD ./requirements.txt /tmp/requirements.txt
ADD ./runtime.txt /tmp/runtime.txt



# Install dependencies
RUN pip install -r /tmp/requirements.txt




# Add our code
ADD ./App /opt/App/
WORKDIR /opt/App

RUN conda config --add channels conda-forge \
    && conda install -c gettsim gettsim 


CMD bokeh serve --port=$PORT --num-procs=0 --allow-websocket-origin=* --address=0.0.0.0 --use-xheaders ./App