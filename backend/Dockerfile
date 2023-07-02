# Base image
FROM python:3.9-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Copy default data for database
WORKDIR /data
COPY ./data .

# Set working directory
WORKDIR /app

# Copy requirement file
COPY ./requirements/requirements.txt /app/requirements.txt

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt

# Copy project files
COPY . .

# Execute entrypoint.sh (collect and copy static + start gunicorn)
RUN chmod +x /app/conf/docker/entrypoint.sh
CMD ["/app/conf/docker/entrypoint.sh"]