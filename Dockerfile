FROM python:3.11.0rc2-bullseye

# Make a directory for the application
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy our source code
COPY /app .

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "-u", "kitchen.py"]