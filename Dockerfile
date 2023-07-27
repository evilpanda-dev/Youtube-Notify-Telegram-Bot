# Use the official Python image as the base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container's working directory
COPY requirements.txt .

# Install the required dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the files from the current directory to the container's working directory
COPY . .


# Define the build arguments with default values (these will be overridden at build time)
ARG MONGO_CONNECTION="MONGO_CONNECTION"
ARG TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
ARG TELEGRAM_GROUP_CHAT_ID="YOUR_TELEGRAM_GROUP_CHAT_ID"

# Set environment variables with the build argument values
ENV MONGO_CONNECTION=${MONGO_CONNECTION}
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV TELEGRAM_GROUP_CHAT_ID=${TELEGRAM_GROUP_CHAT_ID}"

# Expose the port that the Flask app is running on
EXPOSE 8089

# Start the Flask app
CMD ["python", "app.py"]
