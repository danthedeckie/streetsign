FROM python:alpine

# Install packages
RUN apk --no-cache add bash make gcc libc-dev python3-dev imagemagick

# set environment variables so docker uses the virtual environment
ENV VIRTUAL_ENV=./.virtualenv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /usr/src/app

# Copy everything to the image filesystem.
COPY . .
# Run setup script
RUN bash setup.sh

# Tell Docker that this port is used
EXPOSE 5000

# Start application.
CMD ["python3", "./run.py", "waitress"]
