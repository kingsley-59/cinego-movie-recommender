To automatically restart your EC2 server and your FastAPI server running on port 8000 whenever the server goes down, you can set up a service and a process monitor like `systemd` on your EC2 instance. Here are the steps to create a `systemd` service for your FastAPI server:

1. **Create a systemd Service Unit File:**

    First, create a systemd service unit file, typically with a `.service` extension, in the `/etc/systemd/system/` directory. For example, you can create a file named `myfastapi.service`:

    ```bash
    sudo nano /etc/systemd/system/myfastapi.service
    ```

2. **Edit the Service Unit File:**

    Add the following content to your `myfastapi.service` file. Make sure to adjust the `ExecStart` command with the path to your FastAPI application and virtual environment:

    ```plaintext
    [Unit]
    Description=My FastAPI Application
    After=network.target

    [Service]
    ExecStart=python3 /home/ubuntu/cinego-movie-recommender/main.py
    Restart=always
    User=ubuntu
    WorkingDirectory=/home/ubuntu/cinego-movie-recommender

    [Install]
    WantedBy=multi-user.target
    ```

    - `Description`: A description of your service.
    - `ExecStart`: The command to start your FastAPI server. Make sure to replace `/path/to/your/virtualenv` and `/path/to/your/app/directory` with the actual paths.
    - `Restart`: Tells systemd to restart the service always.
    - `User`: Replace `ec2-user` with your actual EC2 instance user.
    - `WorkingDirectory`: Set the working directory for your FastAPI application.
    - `Environment`: Set the environment variables as needed, including `PATH` and `PYTHONPATH`.

3. **Reload systemd and Enable the Service:**

    After creating the service unit file, reload the systemd configuration and enable the service:

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable myfastapi.service
    ```

4. **Start the Service:**

    Start the FastAPI service:

    ```bash
    sudo systemctl start myfastapi.service
    ```

Now, your FastAPI server should be running as a systemd service, and systemd will automatically restart it whenever it goes down for any reason.

Please replace the paths and configurations with the correct values for your specific setup.