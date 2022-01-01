window.addEventListener(
	"load",
	async function () {
		if (window.location.pathname === "/terminal/") {
			const terminalContainer = document.getElementById("terminal-container");
			const term = new Terminal({
				cursorBlink: true,
			});
			const fitAddon = new FitAddon.FitAddon();
			term.loadAddon(fitAddon);
			term.open(terminalContainer);
			fitAddon.fit();

			fetch(window.location.origin + "/get-config")
				.then((response) => response.json())
				.then((data) => {
					if (data.status !== 200) {
						term.write(
							"\r\n=== [CLIENT] ERROR: Could Not Get SSH Configuration ===\r\n"
						);
						return;
					}

					const config = data.config;
					const handshakeData = {
						sshHost: config.host,
						sshPort: config.port,
						sshUsername: config.username,
					};

					if ("password" in config && !config.password === null) {
						console.log(config.password)
						handshakeData.sshPassword = config.password;
					}

					if ("private_key" in config && !config.private_key === null) {
						console.log(config.private_key)
						handshakeData.sshPrivateKey = config.private_key;
					}

					const socket = io({
						query: handshakeData,
					});

					socket.on("connect", async function () {
						term.write(
							"\r\n=== [CLIENT] Connection to Server Established ===\r\n"
						);
					});

					// Browser -> Backend
					term.onKey(function (ev) {
						socket.emit("data", ev.key);
					});

					// Backend -> Browser
					socket.on("data", function (data) {
						term.write(data);
					});

					socket.on("disconnect", async function () {
						term.write(
							"\r\n=== [CLIENT] Connection to Server Terminated ===\r\n"
						);
						term.write("\r\n=== [CLIENT] Retrying... ===\r\n");
					});
				});
		}
	},
	false
);

function enable2FA(csrfToken) {
	fetch(window.location.origin + "/request-2fa")
		.then((response) => response.json())
		.then((data) => {
			if (data.status !== 200) {
				alert("Could not enable 2FA!");
				return;
			}

			const totp = data.code;
			const otp = data.otp;
			const qr = data.qr;

			// alert(
			// 	"Please enter the following secret key into your authenticator app: " +
			// 		totp
			// );
			$("#qr-header").css("display", "block");
			$("#qr-button")
				.css({ display: "block", margin: "0 auto" })
				.attr("onclick", `enterOTP('${otp}', '${totp}', '${csrfToken}')`);
			$("#qr-code").empty();
			new QRCode(document.getElementById("qr-code"), qr);
		});
}

function enterOTP(otp, totp, csrfToken) {
	while (true) {
		const input = prompt("Please enter the generated OTP:");
		if (input !== otp) {
			alert("Invalid OTP! Please try again.");
		} else {
			break;
		}
	}
	alert("2FA successfully enabled.");
	$("#qr-header").css("display", "none");
	$("#qr-button").css({ display: "none" });
	$("#qr-code").empty();
	fetch(window.location.origin + "/enable-2fa/", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
			"X-CSRFToken": csrfToken,
		},
		body: JSON.stringify({
			totp: totp,
		}),
	});
	window.location.reload();
}

function disable2FA() {
	fetch(window.location.origin + "/disable-2fa")
		.then((response) => response.json())
		.then((data) => {
			alert("2FA successfully disabled.");
			window.location.reload();
		});
}
