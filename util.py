from mod_repltalk import client


def verify_headers(headers):
    name = headers.get("X-Replit-User-Name")
    roles = headers.get("X-Replit-User-Roles")

    if name:
        return "moderator" in roles.split(",")
    else:
        return None


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
