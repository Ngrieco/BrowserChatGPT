# # Use an official Python runtime as a parent image
# FROM python:3.9

# # Set the working directory in the container
# WORKDIR /browserchatgpt

# # Copy the local requirements file to the container
# COPY requirements.txt requirements.txt

# # Install any needed packages specified in requirements.txt
# RUN pip install -r requirements.txt

# # Copy the rest of your application's code to the container
# COPY . ./

# # Command to run your application
# CMD [ "streamlit", "run", "streamlit_app.py" ]


# app/Dockerfile

FROM python:3.9

WORKDIR /apps

# Copy the local requirements file to the container
COPY requirements.txt requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "apps/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]