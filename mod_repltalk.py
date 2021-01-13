import repltalk, os


class Post(repltalk.Post):
	async def get_settings(self):
		client = self.client
		r = await client.perform_graphql(
			'post',
			repltalk.Queries.get_post_settings,
			id=self.id,
		)
		return r

	async def update(self, is_announcement=None, is_pinned=None, is_locked=None, is_hidden=None):
		settings = await self.get_settings()
		client = self.client
		if is_announcement == None: is_announcement = 'announcement' if settings['isAnnouncement'] else None
		else: is_announcement = 'announcement' if is_announcement else None
		r = await client.perform_graphql(
			'updatePost',
			repltalk.Queries.update_post,
			input={
				'id': self.id,
				'postType': is_announcement,
				'isPinned': is_pinned if is_pinned != None else settings['isPinned'],
				'isLocked': is_locked if is_locked != None else settings['isLocked'],
				'isHidden': is_hidden if is_hidden != None else settings['isHidden'],
			}
		)
		return r

	async def delete(self):
			client = self.client
			r = await client.perform_graphql(
				'deletePost',
				repltalk.Queries.delete_post,
				id=self.id,
			)
			return r
	repltalk.Post.delete = delete



class Comment(repltalk.Comment):
	async def _get_comment(self, id):
		return await self.perform_graphql(
			'comment',
			repltalk.Queries.get_comment,
			id=id
		)


	async def delete(self):
		client = self.client
		r = await client.perform_graphql(
			'deleteComment',
			repltalk.Queries.delete_comment,
			id=self.id,
		)
		return r



class User(repltalk.User):
	async def ban(self, reason):
		client = self.client
		r = await client.perform_graphql(
			'Mutation',
			repltalk.Queries.ban_user,
			user=self.name,
			reason=reason,
		)
		return r



class Client(repltalk.Client):
	async def get_audit(self, id):
		r = await self.perform_graphql(
			'Query',
			repltalk.Queries.get_audit,
			id=id
		)
		data = {}
		for key in range(len(r['moderator']['audit']['viewItem']['rows'])):
			data[r['moderator']['audit']['viewItem']['rows'][key]['key']] = r['moderator']['audit']['viewItem']['rows'][key]['value']
		return data

	async def _get_audits(self, creator, model, actionType, page, order):	
		r = await self.perform_graphql(
			'Query',
			repltalk.Queries.get_audits,
			creator=creator,
			model=model,
			actionType=actionType,
			page=page,
			order=order
		)
		return r
	
	async def get_audits(self, creator=None, model=None, actionType=None, page=1, order="NEWEST"):
		data = await self._get_audits(creator, model, actionType, page, order)
		auditList = []
		for row in range(len(data['moderator']['audit']['viewAudit']['rows'])):
			if data['moderator']['audit']['viewAudit']['rows'][row] != {} and data['moderator']['audit']['viewAudit']['rows'][row]['id'] != 'Page':
				creator = await client.get_user(data['moderator']['audit']['viewAudit']['rows'][row]['creator'])
				model = data['moderator']['audit']['viewAudit']['rows'][row]['model']
				type = data['moderator']['audit']['viewAudit']['rows'][row]['type']
				created = data['moderator']['audit']['viewAudit']['rows'][row]['created']
				id = data['moderator']['audit']['viewAudit']['rows'][row]['id']
				if type == 'DELETE' and model in ['Posts', 'Comments']:
					attached =  data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
					type = 'DELETED'
				else:
					if model == 'Posts':
						try:
							attached = await client.get_post(data['moderator']['audit']['viewAudit']['rows'][row]['targetId'])
						except repltalk.PostNotFound:
							attached = data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
					elif model == 'Comments':
						try:
							attached = await client.get_comment(data['moderator']['audit']['viewAudit']['rows'][row]['targetId'])
						except repltalk.CommentNotFound:
							attached = data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
					elif model == 'BoardReports':
						attached = data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
						#attached = await client.get_report(data['moderator']['audit']['viewAudit']['rows'][row]['targetId'])
					elif model == 'Warning':
						try:
							attached = await client.get_user_by_id(data['moderator']['audit']['viewAudit']['rows'][row]['targetId'])
						except:
							attached = data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
					elif model == 'BannedBoardUsers':
						try:
							attached = await client.get_user_by_id(data['moderator']['audit']['viewAudit']['rows'][row]['targetId'])
						except:
							attached = data['moderator']['audit']['viewAudit']['rows'][row]['targetId']
				auditList.append({
					'id': id,
					'creator': creator,
					'model': model,
					'type': type,
					'created': created,
					'attached': attached
				})
		return auditList



class Queries(repltalk.Queries):
	get_post_settings = '''
		query post($id: Int!) {
			post(id: $id) {
				id
				...PostSettingsPost
				__typename
			}
		}
		
		fragment PostSettingsPost on Post {
			id
			canPin
			canSetType
			canLock
			canHide
			canChangeBoard
			canComment
			isAnnouncement
			isPinned
			isLocked
			isHidden
			board {
				id
				name
				__typename
			}
			__typename
		}
	'''

	update_post = '''
		mutation updatePost($input: UpdatePostInput!) {
			updatePost(input: $input) {
				post {
					id
					...PostSettingsPost
					__typename
				}
				__typename
			}
		}
		
		fragment PostSettingsPost on Post {
			id
			canPin
			canSetType
			canLock
			canHide
			canChangeBoard
			canComment
			isAnnouncement
			isPinned
			isLocked
			isHidden
			board {
				id
				name
				__typename
			}
			__typename
		}
	'''

	delete_post = '''
		mutation deletePost($id: Int!) {
			deletePost(id: $id) {
				id
				__typename
			}
		}
	'''

	delete_comment = '''
		mutation deleteComment($id: Int!) {
			deleteComment(id: $id) {
				id
				__typename
			}
		}
	'''

	ban_user = '''
		mutation Mutation($user: String!, $reason: String) {
			clui {
				moderator {
					user {
						ban(user: $user, reason: $reason) {
							...CluiOutput
							__typename
						}
						__typename
					}
					__typename
				}
				__typename
			}
		}
		
		fragment CluiOutput on CluiOutput {
			... on CluiSuccessOutput {
				message
				json
				__typename
			}
			... on CluiErrorOutput {
				error
				json
				__typename
			}
			... on CluiMarkdownOutput {
				markdown
				__typename
			}
			... on CluiTableOutput {
				columns {
					label
					key
					__typename
				}
				rows
				__typename
			}
			__typename
		}
	'''

	get_audits = '''
		query Query($creator: String, $model: ModeratorAuditModels, $actionType: ModeratorAuditActionType, $page: Int, $order: ModeratorAuditSorting) {
			clui {
				moderator {
					audit {
						viewAudit(creator: $creator, model: $model, actionType: $actionType, page: $page, order: $order) {
							...CluiOutput
							__typename
						}
						__typename
					}
					__typename
				}
				__typename
			}
		}
		
		fragment CluiOutput on CluiOutput {
			... on CluiSuccessOutput {
				message
				json
				__typename
			}
			... on CluiErrorOutput {
				error
				json
				__typename
			}
			... on CluiMarkdownOutput {
				markdown
				__typename
			}
			... on CluiTableOutput {
				columns {
					label
					key
					__typename
				}
				rows
				__typename
			}
			__typename
		}
	'''

	get_audit = '''
		query Query($id: Int!) {
			clui {
				moderator {
					audit {
						viewItem(id: $id) {
							...CluiOutput
							__typename
						}
						__typename
					}
					__typename
				}
				__typename
			}
		}
	
		fragment CluiOutput on CluiOutput {
			... on CluiSuccessOutput {
				message
				json
				__typename
			}
			... on CluiErrorOutput {
				error
				json
				__typename
			}
			... on CluiMarkdownOutput {
				markdown
				__typename
			}
			... on CluiTableOutput {
				columns {
					label
					key
					__typename
				}
				rows
				__typename
			}
		__typename
		}
	'''


repltalk.Queries = Queries
repltalk.Post = Post
repltalk.Comment = Comment
repltalk.User = User
repltalk.Client = Client


client = repltalk.Client()
client.sid=os.getenv('sid')