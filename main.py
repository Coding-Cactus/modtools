import flask, asyncio
from mod_repltalk import repltalk, client
import infractions


app = flask.Flask(__name__)


@app.route('/')
def main():
	if 'X-Replit-User-Name' in flask.request.headers:
		if flask.request.headers['X-Replit-User-Name'] != '':
			if 'moderator' in flask.request.headers['X-Replit-User-Roles'].split(','):
				return flask.render_template('mod.html')
			return 'no'
	return flask.render_template('index.html')




#--------------------------------------------------------------------
#                             admin ban                              
#--------------------------------------------------------------------


async def _ban(username, reason):
	user = await client.get_user(username)
	if str(user) != 'None':
		posts = await user.get_posts()
		while len(list(posts)) > 0:
			for post in posts:
				await post.delete()
			posts = await user.get_posts()
		comments = await user.get_comments()
		while len(list(comments)) > 0:
			for comment in comments:
				await comment.delete()
			comments = await user.get_comments()
		await user.ban(reason)
		return True
	else:
		return False

@app.route('/admin-ban', methods=['POST'])
def ban():
	if 'X-Replit-User-Name' in flask.request.headers:
		if flask.request.headers['X-Replit-User-Name'] != '':
			if 'moderator' in flask.request.headers['X-Replit-User-Roles'].split(','):
				username = flask.request.form['username']
				reason = flask.request.form['reason']
				result = asyncio.run(_ban(username, reason))
				if not result:
					return "User not found"				
				if len(reason) == 0:
					return "Must provide a reason"
				if result:
					return username + " has now been banned and all posts deleted"
			return 'no'
	return flask.render_template('index.html')


@app.route('/audits', methods=['GET', 'POST'])
def audits():
	if 'X-Replit-User-Name' in flask.request.headers:
		if flask.request.headers['X-Replit-User-Name'] != '':
			if 'moderator' in flask.request.headers['X-Replit-User-Roles'].split(','):
				if flask.request.method == 'POST':
					settings = {}
					settings['creator'] = flask.request.form['creator'] if flask.request.form['creator'] != '' else None
					settings['actionType'] = flask.request.form['actionType'] if flask.request.form['actionType'] != 'ALL' else None
					settings['model'] = flask.request.form['model'] if flask.request.form['model'] != 'ALL' else None
					settings['page'] = int(flask.request.form['page']) if flask.request.form['page'] != '' else 1
					settings['order'] = flask.request.form['order'] if flask.request.form['order'] != '' else "NEWEST"
					audits = asyncio.run(client.get_audits(creator=settings['creator'], model=settings['model'], actionType=settings['actionType'], page=int(settings['page']), order=settings['order']))
					settings['creator'] = flask.request.form['creator'] if flask.request.form['creator'] != None else ''
					settings['actionType'] = flask.request.form['actionType'] if flask.request.form['actionType'] != None else 'ALL'
					settings['model'] = flask.request.form['model'] if flask.request.form['model'] != None else 'ALL'
				else:
					settings = {}
					settings['page'] = 1
					audits = asyncio.run(client.get_audits())
				for audit in range(len(audits)):
					auditData = asyncio.run(client.get_audit(audits[audit]['id']))
					if 'resolved' in auditData:
						if auditData['resolved']: audits[audit]['type'] = "RESOLVED"
						elif not auditData['resolved']: audits[audit]['type'] = "UNRESOLVED"
					elif 'is_hidden' in auditData:
						if auditData['is_hidden']: audits[audit]['type'] = "UNLISTED"
						elif not auditData['is_hidden']: audits[audit]['type'] = "RELISTED"
					elif 'is_locked' in auditData:
						if auditData['is_locked']: audits[audit]['type'] = "LOCKED"
						elif not auditData['is_locked']: audits[audit]['type'] = "UNLOCKED"
					elif 'is_pinned' in auditData:
						if auditData['is_pinned']: audits[audit]['type'] = "PINNED"
						elif not auditData['is_pinned']: audits[audit]['type'] = "UNPINNED"
					elif 'is_announcement' in auditData:
						if auditData['is_announcement']: audits[audit]['type'] = "MARKED AS ANNOUNCEMENT"
						elif not auditData['is_announcement']: audits[audit]['type'] = "UNMARKED AS ANNOUNCEMENT"
					elif 'board_id' in auditData: audits[audit]['type'] = "CHANGED BOARD"
					elif auditData['Model'] == "BannedBoardUsers":
						if auditData['Type'] == "CREATE": audits[audit]['type'] = "BANNED"
						if auditData['Type'] == "DELETE": audits[audit]['type'] = "UNBANNED"
					elif auditData['Model'] == "Warning":
						if auditData['Type'] == "CREATE": audits[audit]['type'] = "WARNED"
						if auditData['Type'] == "DELETE": audits[audit]['type'] = "REMOVED WARNING"
					if not str(audits[audit]['attached']).isdigit() and audits[audit]['model'] in ['Posts', 'Comments']:
						audits[audit]['attached'] = audits[audit]['attached'].url
					elif not str(audits[audit]['attached']).isdigit() and audits[audit]['model'] == 'BannedBoardUsers':
						audits[audit]['attached'] = audits[audit]['attached'].name
					elif not str(audits[audit]['attached']).isdigit() and audits[audit]['model'] == 'Warning':
						audits[audit]['attached'] = audits[audit]['attached'].name
					audits[audit]['creator'] = audits[audit]['creator'].name
				return flask.render_template('audits.html', audits=audits, settings=settings, str=lambda i:str(i))
			return 'no'
	return flask.render_template('index.html')



@app.route('/auto-act', methods=['POST'])
def auto_act():
	if 'X-Replit-User-Name' in flask.request.headers:
		if flask.request.headers['X-Replit-User-Name'] != '':
			if 'moderator' in flask.request.headers['X-Replit-User-Roles'].split(','):
				type = flask.request.form['type']
				if type not in infractions:
					return 'Invalid Type'
				target = flask.request.form[type+'-input']
				if type in ['post', 'comment']:
					try:
						target = int(target)
					except ValueError:
						return 'ID must be a number'
				if type == 'post':
					target = asyncio.run(client.get_post(target))
				elif type == 'comment':
					target = asyncio.run(client.get_comment(target))
				elif type == 'user':
					target = asyncio.run(client.get_user(target))
				infraction = flask.request.form[type+'-infraction-input'].lower()
				if infraction not in infractions[type]:
					return 'Invalid infraction'
				level = infractions[type][infraction]
				if level == 1:
					pass
			return 'no'
	return flask.render_template('index.html')

app.run('0.0.0.0')