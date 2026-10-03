FROM python:3.12-slim

#Setting working directory inside the container
WORKDIR $HOME/app

#Copy all the files from current directory to container's working directory
COPY . .

# Install the dependencies from the requirements file without using cache to reduce image size
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Define the command to run the Flask app using Gunicorn with 2 worker processes
# - "-w 2": Use 2 worker processes for handling requests
# - "-b 0.0.0.0:7860": Bind the server to port 7860 on all network interfaces
# - "app:lead_conversion_predictor_api": the Flask object named lead_conversion_predictor_api inside app.py
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:7860", "app:lead_conversion_predictor_api"]
