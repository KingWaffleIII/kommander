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
		const config = socket.request;

		const conn = new SSHClient();

		conn
			.on("ready", function () {
				socket.emit(
					"data",
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
			})
			if (!config._query["sshPrivateKey"]) {
				conn.connect({
					host: config._query["sshHost"],
					port: config._query["sshPort"],
					username: config._query["sshUsername"],
					password: config._query["sshPassword"],
				});	
			} else {
				conn.connect({
					host: config._query["sshHost"],
					port: config._query["sshPort"],
					username: config._query["sshUsername"],
					password: config._query["sshPassword"],
					privateKey: config._query["sshPrivateKey"],	
				});
			}
	});
}

const PORT = args["port"] || 9000;

http.listen(PORT, async () => {
	console.log(`Listening on http://localhost:${PORT}`);
	await main();
});
