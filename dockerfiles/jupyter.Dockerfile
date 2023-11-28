FROM jupyter/minimal-notebook:notebook-7.0.3

RUN pip install --upgrade pip

USER root 
#RUN sudo apt-get update
USER jovyan

COPY dockerfiles/requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /home/jovyan/work/

CMD ["jupyter-notebook", "--notebook-dir=/home/jovyan/work/", "--ip='0.0.0.0'", "--port=8888","--NotebookApp.token=''","--allow-root"]

# BUILD docker build -f dockerfiles/jupyter.Dockerfile -t linux-commits:0.1.0 .