# Use an official Python runtime as a parent image.
# This is a multi-architecture image that works on Raspberry Pi (ARM64).
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies that might be needed for certain Python packages
# (e.g., psycopg2-binary might need some of these)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker's layer caching
# CORRECTED PATH: The file is in the root of the build context.
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project directory into the container
# This includes Home.py, pages/, .streamlit/, etc.
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8501

# The command to run the Streamlit app when the container launches.
# It runs on all available network interfaces inside the container.
CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.address=0.0.0.0"]
