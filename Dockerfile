FROM debian:10-slim

# Suppress interactive prompts.
ENV DEBIAN_FRONTEND=noninteractive

# Required: Install utilities required by Spark scripts.
RUN apt-get update && \
    apt-get install -y wget procps tini

# Optional: Add extra jars.
ENV SPARK_EXTRA_JARS_DIR=/opt/spark/jars/
ENV SPARK_EXTRA_CLASSPATH='/opt/spark/jars/*'
RUN mkdir -p "${SPARK_EXTRA_JARS_DIR}"

# Optional: Install and configure Miniconda3.
ENV CONDA_HOME=/opt/miniconda3
ENV PYSPARK_PYTHON=${CONDA_HOME}/bin/python
ENV PYSPARK_DRIVER_PYTHON=${CONDA_HOME}/bin/python

ENV PATH=${CONDA_HOME}/bin:${PATH}
RUN wget -O miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash miniconda.sh -b -p /opt/miniconda3 \
  && ${CONDA_HOME}/bin/conda config --system --set always_yes True \
  && ${CONDA_HOME}/bin/conda config --system --set auto_update_conda False \
  && ${CONDA_HOME}/bin/conda config --system --prepend channels conda-forge \
  && ${CONDA_HOME}/bin/conda config --system --set channel_priority strict

# Optional: Install Conda packages.
#
# The following packages are installed in the default image. It is strongly
# recommended to include all of them.
#
# For Production use it would be best to lock the versions if those packages are critical
#
# Use mamba to install packages quickly.
RUN ${CONDA_HOME}/bin/conda install mamba -n base -c conda-forge \
    && ${CONDA_HOME}/bin/mamba install \
      conda \
      cython \
      fastavro \
      fastparquet \
      gcsfs \
      google-cloud-bigquery-storage \
      google-cloud-bigquery[pandas] \
      google-cloud-bigtable \
      google-cloud-container \
      google-cloud-datacatalog \
      google-cloud-dataproc \
      google-cloud-datastore \
      google-cloud-language \
      google-cloud-logging \
      google-cloud-monitoring \
      google-cloud-pubsub \
      google-cloud-redis \
      google-cloud-spanner \
      google-cloud-speech \
      google-cloud-storage \
      google-cloud-texttospeech \
      google-cloud-translate \
      google-cloud-vision \
      koalas \
      matplotlib \
      nltk \
      numba \
      numpy \
      openblas \
      orc \
      pandas \
      pyarrow \
      pysal \
      pytables \
      python \
      regex \
      requests \
      rtree \
      scikit-image \
      scikit-learn \
      scipy \
      seaborn \
      sqlalchemy \
      sympy \
      virtualenv

### !!!Try not to chnage everything above this line often as build time can be extensive!!! ###

# Optional: Add extra Python modules.
ENV PYTHONPATH=/opt/python/packages
RUN mkdir -p "${PYTHONPATH}"

# Add additional jars to here if required
#COPY *.jar "${SPARK_EXTRA_JARS_DIR}"

# Add additional python modules if required
#COPY test_util.py "${PYTHONPATH}"

# Required: Create the 'yarn_docker_user' group/user.
# The GID and UID must be 1099. Home directory is required.
RUN groupadd -g 1099 yarn_docker_user
RUN useradd -u 1099 -g 1099 -d /home/yarn_docker_user -m yarn_docker_user
USER yarn_docker_user