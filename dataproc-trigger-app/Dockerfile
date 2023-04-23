# Use the official Python 3.8 image as the base image
FROM python:3.8-slim

ARG APP_HOME=/home/app

# Add user
RUN groupadd -g 999 app && useradd -r -u 999 -g app app

# Create and set the working directory
WORKDIR ${APP_HOME}

# change permission to app user
RUN chown -R app:app ${APP_HOME}

# change to app user
USER app

# Copy requirements.txt and install the required Python packages
COPY requirements.txt .
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate && pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt"

# Copy the application code
COPY app.py .
COPY gunicorn_config.py .
COPY static static
COPY templates templates

# Expose the port the app runs on
EXPOSE 8080

# Start Gunicorn with the app module
CMD ["/home/app/venv/bin/gunicorn", "--config", "gunicorn_config.py", "app:app"]