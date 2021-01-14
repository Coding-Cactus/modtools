import util
import json
import flask
import asyncio

from mod_repltalk import client
from mod_repltalk import repltalk

from flask import request
from flask import render_template


app = flask.Flask(__name__)

DENY = "You are not a ReplTalk moderator! =P"
BAN = "{name} has now been banned and all posts/comments were deleted."
LOGIN = "You are not logged with your Replit account!"
INVALID = "The given {value} is invalid."

with open("infractions.json", "r") as f:
		infractions = json.load(f)


@app.route("/")
def main():
		head = request.headers
		flag = util.verify_headers(head)

		if flag:
				return render_template("mod.html")
		elif flag == False:
				return DENY, 403
		else:
				return render_template("index.html")


@app.route("/admin-ban", methods=["POST"])
def ban():
		form = request.form
		head = request.headers

		flag = util.verify_headers(head)

		if flag:
				reason = form["reason"]
				username = form["username"]

				result = asyncio.run(util._ban(username, reason))

				if not result:
						return "User not found.", 404

				if not reason:
						return "Must provide a valid reason.", 400

				if result:
						return BAN.format(username), 204
		elif flag == False:
				return DENY, 403
		else:
				return render_template("index.html")


@app.route("/audits", methods=["GET", "POST"])
def audits():
		form = request.form
		head = request.headers

		flag = util.verify_headers(head)

		if flag:
				if flask.request.method == "POST":
						settings = {
								"creator": form.get("creator", None),
								"actionType": form.get("actionType", None),
								"model": form.get("model", None),
								"page": form.get("page", 1),
								"order": form.get("order", "NEWEST"),
						}

						settings["page"] = int(settings["page"]) if settings["page"] != "" else 1

						audits = asyncio.run(
								client.get_audits(
										creator=settings["creator"] if settings["creator"] != "" else None,
										model=settings["model"] if settings["model"] != "ALL" else None,
										actionType=settings["actionType"] if settings["actionType"] != "ALL" else None,
										page=settings["page"],
										order=settings["order"],
								)
						)

				else:
						settings = {"page": 1}
						audits = asyncio.run(client.get_audits())

				for audit in range(len(audits)):
						auditData = asyncio.run(client.get_audit(audits[audit]["id"]))

						if "resolved" in auditData:
								if auditData["resolved"]:
										audits[audit]["type"] = "RESOLVED"
								elif not auditData["resolved"]:
										audits[audit]["type"] = "UNRESOLVED"
						elif "is_hidden" in auditData:
								if auditData["is_hidden"]:
										audits[audit]["type"] = "UNLISTED"
								elif not auditData["is_hidden"]:
										audits[audit]["type"] = "RELISTED"
						elif "is_locked" in auditData:
								if auditData["is_locked"]:
										audits[audit]["type"] = "LOCKED"
								elif not auditData["is_locked"]:
										audits[audit]["type"] = "UNLOCKED"
						elif "is_pinned" in auditData:
								if auditData["is_pinned"]:
										audits[audit]["type"] = "PINNED"
								elif not auditData["is_pinned"]:
										audits[audit]["type"] = "UNPINNED"
						elif "is_announcement" in auditData:
								if auditData["is_announcement"]:
										audits[audit]["type"] = "MARKED AS ANNOUNCEMENT"
								elif not auditData["is_announcement"]:
										audits[audit]["type"] = "UNMARKED AS ANNOUNCEMENT"
						elif "board_id" in auditData:
								audits[audit]["type"] = "CHANGED BOARD"
						elif auditData["Model"] == "BannedBoardUsers":
								if auditData["Type"] == "CREATE":
										audits[audit]["type"] = "BANNED"
								if auditData["Type"] == "DELETE":
										audits[audit]["type"] = "UNBANNED"
						elif auditData["Model"] == "Warning":
								if auditData["Type"] == "CREATE":
										audits[audit]["type"] = "WARNED"
								if auditData["Type"] == "DELETE":
										audits[audit]["type"] = "REMOVED WARNING"

						if (
								not str(audits[audit]["attached"]).isdigit()
								and audits[audit]["model"] in ["Posts", "Comments"]
						): audits[audit]["attached"] = audits[audit]["attached"].url

						elif (
								not str(audits[audit]["attached"]).isdigit()
								and audits[audit]["model"] == "BannedBoardUsers"
						): audits[audit]["attached"] = audits[audit]["attached"].name

						elif (
								not str(audits[audit]["attached"]).isdigit()
								and audits[audit]["model"] == "Warning"
						): audits[audit]["attached"] = audits[audit]["attached"].name


						audits[audit]["creator"] = audits[audit]["creator"].name
				
				return flask.render_template(
						"audits.html", audits=audits, settings=settings, str=lambda i: str(i)
				)

		elif flag == False:
				return DENY, 403
		else:
				return flask.render_template("index.html")


@app.route("/auto-act", methods=["POST"])
def auto_act():
		form = request.form
		head = request.headers

		flag = util.verify_headers(head)

		if flag:
				type = form.get("type")

				if type not in infractions:
						INVALID.format(value=type)
				
				target = form[type + "-input"]

				if type in ["post", "comment"]:
						try:
								target = int(target)
						except ValueError:
								return INVALID.format(value="ID")
				
				
				method = getattr(client, f"get_{type}", default=None)

				if method:
						target = asyncio.run(method(target))
				else:
						return flask.abort(400)
				
				infraction = flask.request.form[type + "-infraction-input"].lower()

				if infraction not in infractions[type]:
						return "The infraction type is invalid.", 400

				level = infractions[type][infraction]
				if level == 1: pass

		elif flag == False:
				return DENY
		else:
				return flask.render_template("index.html")


app.run(host="0.0.0.0", port=8080, threaded=True)
