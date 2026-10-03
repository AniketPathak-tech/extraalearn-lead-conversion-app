# Use a minimal base image with Python 3.12 installed
FROM python:3.12-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Copy all files from the current directory on the host to the container's /app directory
COPY . .

# Install the Python dependencies listed in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Define the command to run the Streamlit app on port 8501 and make it accessible externally
# - "--server.address=0.0.0.0": listen on all network interfaces
# - "--server.enableXsrfProtection=false": avoids blocked requests when the app is served behind a proxy
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
