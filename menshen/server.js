const args = require("minimist")(process.argv.slice(2));

const express = require("express");
const app = express();

const http = require("http").Server(app);
const io = require("socket.io")(http, {
	cors: {
		origin: "*",
	},
});

const { readFileSync } = require("fs");

const SSHClient = require("ssh2").Client;

async function main() {
	io.on("connection", function (socket) {
		console.log(`\r\n=== [SERVER] Connection to Client Established ===\r\n`);

		const config = socket.request;

		const conn = new SSHClient();

		conn
			.on("ready", function () {
				socket.emit(
					"data",
					`\r\n=== [SERVER] Connection to ${config._query["sshHost"]} Established ===\r\n`
				);
				console.log(
					`\r\n=== [SERVER] Connection to ${config._query["sshHost"]} Established ===\r\n`
				);

				conn.shell(function (err, stream) {
					if (err)
						return socket.emit(
							"data",
							`\r\n=== [SERVER] ERROR: ${err.message} ===\r\n`
						);
					socket.on("data", function (data) {
						stream.write(data);
					});
					stream
						.on("data", function (d) {
							socket.emit("data", d.toString("binary"));
						})
						.on("close", function () {
							conn.end();
						});
				});
			})
			.on("close", async function () {
				socket.emit(
					"data",
					`\r\n=== [SERVER] Connection to ${config._query["sshHost"]} Terminated ===\r\n`
				);
				socket.emit(
					"data",
					`\r\n=== [SERVER] Refresh Page to Reconnect ===\r\n`
				);
			})
			.on("error", function (err) {
				socket.emit("data", `\r\n=== [SERVER] ERROR: ${err.message} ===\r\n`);
			});

		socket.on("disconnect", function () {
			console.log(`\r\n=== [SERVER] Connection to Client Terminated ===\r\n`);
		});

		let connConfig = {
			host: config._query["sshHost"],
			port: config._query["sshPort"],
			username: config._query["sshUsername"],
			debug: console.log,
			algorithms: {
				kex: [
					"diffie-hellman-group1-sha1",
					"ecdh-sha2-nistp256",
					"ecdh-sha2-nistp384",
					"ecdh-sha2-nistp521",
					"diffie-hellman-group-exchange-sha256",
					"diffie-hellman-group14-sha1",
				],
			},
		};
		if (config._query["sshPrivateKey"]) {
			connConfig.privateKey = config._query["sshPrivateKey"];
		} else if (config._query["sshPassword"]) {
			connConfig.password = config._query["sshPassword"];
		}
		conn.connect(connConfig);
	});
}

const PORT = args["port"] || 9000;

http.listen(PORT, async () => {
	console.log(`Listening on http://localhost:${PORT}`);
	await main();
});
