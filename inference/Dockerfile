FROM nvcr.io/nvidia/pytorch:24.08-py3

# Set the working directory in the container
WORKDIR /clip_rt

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /clip_rt
COPY . .

# Run app.py when the container launches
# Add -u to unbuffer the output
# Use entrypoint to override nvidia's default command
ENTRYPOINT ["python3", "-u", "src/app.py"]

