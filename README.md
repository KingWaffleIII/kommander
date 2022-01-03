# Kommander

**A simple web-based SSH client.**
**It supports:**

- **entering SSH login details (including private key and custom ports) and connecting**
- **user authentication (and 2FA!)**
- **saving configurations to access them from anywhere**

**Kommander is built on Django and Python and handles the user authentication, 2FA, storing configuration and the views.**
**Menshen is built on Express, Xterm.js, Socket.io, SSH2 and Node.JS.**

## Install

**Simply clone the repository:**

> git clone https://github.com/KingWaffleIII/kommander.git

**Kommander depends on Python v3.8+!**

## Configuration

### Nginx

**Kommander is reliant on Nginx so you must setup a configuration file or edit an existing one to server Kommander. Use the following as a template:**

```txt
server {
	root /usr/share/nginx/html;
    server_name _;

    listen [::]:80;
    listen 80;

    # /STATIC IS NECESSARY

	location /static {
		expires -1;
		alias /usr/share/nginx/html/static;
	}

    # /SOCKET.IO IS NECESSARY

	location /socket.io {
        # choose whatever port you need - run.sh needs to run on the same port

		proxy_pass http://localhost:9000;
	}

	location / {
        # choose whatever port you need - run.sh needs to run on the same port

		proxy_pass http://localhost:8000;
	}
}
```

### `kommander/settings.py`

**You must fill out the `CSRF_TRUSTED_ORIGINS` list in `kommander/settings.py` with your domain(s). An example of this is commented out in the same file.**

### SMTP

**Django has support for password reset emails. To use this feature, you must fill in the details of an email account in `kommander/email_config.json`.**
**Additionally, you must also change `init_sites.py` and replace `kommander.planetwaffle.net` with your own production domain and `dev.planetwaffle.net` with your own development domain. These can be `http://localhost`.**

### Superuser Account

**You must also change the environment variables in `run.sh` for `python3.10 manage.py createsuperuser --no-input` to your preference to set the Django administrator account. You need to supply an email and a password.**

## Usage

**Simply run the `run.sh` bash script. It takes the following parameters:**

> `-i`: installs dependencies from the `package-lock.json` and `requirements.txt`. <br>
> It accepts `yes` or `no`.

> `-m`: whether or not to enable developer mode. This will set `kommander.settings.DEBUG` to True, which is not appropriate for production, as well as define which site to use in `init_sites.py`.
> Anything that isn't `dev` will be assumed to run in production mode.

> `-p`: the port that the Django server should run on.

> `-a`: the port that the SSH gateway server should run on.

> `-s`: whether or not to enable silent mode. This will disable all requests for input.
> Anything that isn't `yes` will be treated as `no`.

## Menshen

**Menshen is the underlying server that powers Kommander. It is the service that acts as a gateway (hence the name 'Menshen', after the Chinese divine guardians of doors and gates) between the user and the remote server.**

## Contributing

**Contributions are welcome! If you find any issues, improvements or would like a feature added, feel free to submit an issue or a pull request.**
**Please keep in mind, however, that Kommander is a _simple_ web-based SSH client. I feel that v1.0.0 successfully meets all the criteria for a simple SSH client and therefore, am unlikely to add any new features. I will be happy to review any pull requests though.**

If your issue is to do with an SSH connection failing, please submit the output of Menshen from the console in your issue since it will help in locating the problem. The output should look similar to:

```
=== [SERVER] Connection to Client Established ===

Custom crypto binding available
Local ident: 'SSH-2.0-ssh2js1.5.0'
Client: Trying localhost on port 22 ...
Socket error: connect ECONNREFUSED 127.0.0.1:22
Socket closed

=== [SERVER] Connection to Client Terminated ===
```

## License

**Kommander and Menshen are released under the [MIT license](https://opensource.org/licenses/MIT).**

```

```
