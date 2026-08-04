# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install uv directly
RUN pip install uv

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Use uv to install dependencies globally (no virtual environment)
RUN uv pip install --system -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

WORKDIR /app/app

# Tell Python where the root of your modules are
ENV PYTHONPATH=/app/app

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" , "--reload"]