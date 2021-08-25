import sys
import json
import pandas as pd
import plotly.offline as py
import plotly.graph_objs as go
from datetime import datetime

def get_convo_data(conversation):
	"""lookup table for user_id"""
	userid2name = {}
	with open(conversation, encoding='utf-8') as data_file:
		data=json.load(data_file)
	for member in data['members']:
		userid2name[member['user_id']] = member['name']
	return userid2name

userid2name = get_convo_data('conversation.json')

def likes_by_id(message):
	"""gathers likes by message"""
	likes_received_by_id = {}
	likes_given_by_id = {}
	msg_cnt_by_id = {}
	likes_per_msg = []
	with open(message, encoding='utf-8') as data_file:
		data=json.load(data_file)
	for msg in data:
		msg_likes = []
		#after 8/1/20
		if (msg['created_at'] < 0):
		  continue
		msg_likes.append(msg['created_at'])
		msg_likes.append(msg['user_id'])
		msg_likes.append(len(msg['favorited_by']))
		#likes_per_msg.append([msg['created_on'], msg['user_id'], len(msg['favorited_by']])
		likes_per_msg.append(msg_likes)
		likes_received_by_id[msg['user_id']] = likes_received_by_id.get(msg['user_id'], 0) + len(msg['favorited_by'])
		msg_cnt_by_id[msg['user_id']] = msg_cnt_by_id.get(msg['user_id'], 0) + 1
		for liker in msg['favorited_by']:
			likes_given_by_id[liker] = likes_given_by_id.get(liker, 0) + 1
	return likes_given_by_id, likes_received_by_id, msg_cnt_by_id, likes_per_msg


def ts2date(ts):
	"""To do: this can be used to get likes by day, currently killed that"""
	return pd.Series([datetime.utcfromtimestamp(0).strftime('%Y-%m-%d')])
	
def df_total_msg_by_user_id(cdata, mdata):
	"""returns data frame for mgs count by user id"""
	dfc = pd.DataFrame(list(cdata.items()), columns=['user_id', 'name'])
	dfm0 = pd.DataFrame(list(mdata[0].items()), columns=['user_id', 'likes_given'])
	dfm1 = pd.DataFrame(list(mdata[1].items()), columns=['user_id', 'likes_received'])
	dfm2 = pd.DataFrame(list(mdata[2].items()), columns=['user_id', 'msg_cnt'])
	return dfm2
	
def df_likes_per_user_per_day(cdata, mdata):
	"""todo: likes per day scatter - unused at the moment"""
	dfc = pd.DataFrame(list(cdata.items()), columns=['user_id', 'name'])
	dfm0 = pd.DataFrame(list(mdata[0].items()), columns=['user_id', 'likes_given'])
	dfm1 = pd.DataFrame(list(mdata[1].items()), columns=['user_id', 'likes_received'])
	dfm2 = pd.DataFrame(list(mdata[2].items()), columns=['user_id', 'msg_cnt'])
	dfm3 = pd.DataFrame(mdata[3], columns=['ts', 'user_id', 'msg_likes'])
	dfm3['day'] = dfm3.apply(lambda x: ts2date(x['ts']), axis=1)
	#dfm3['day'] = datetime.utcfromtimestamp(dfm3['ts']).strftime('%Y-%m-%d')
	df = dfc.merge(dfm0, how="right").merge(dfm1).merge(dfm2)
	df['likes_per_msg'] = df['likes_received']/df['msg_cnt']
	days = dfm3.groupby(['user_id', 'day'])['msg_likes'].sum().reset_index()
	days = days.merge(dfc)
	return days
	
def df_likes_per_username(cdata, mdata):
	"""Makes stat2 likes by username"""
	dfc = pd.DataFrame(list(cdata.items()), columns=['user_id', 'name'])
	dfm3 = pd.DataFrame(mdata[3], columns=['ts', 'user_id', 'msg_likes'])
	days = dfm3.groupby(['user_id'])['msg_likes'].sum().reset_index()
	days = days.merge(dfc)
	return days
	
def df_like_ratios(cdata, mdata):
	"""Makes stat3 like ratios and given vs received"""
	dfc = pd.DataFrame(list(cdata.items()), columns=['user_id', 'name'])
	dfm0 = pd.DataFrame(list(mdata[0].items()), columns=['user_id', 'likes_given'])
	dfm1 = pd.DataFrame(list(mdata[1].items()), columns=['user_id', 'likes_received'])
	dfm2 = pd.DataFrame(list(mdata[2].items()), columns=['user_id', 'msg_cnt'])
	df = dfc.merge(dfm0, how="right").merge(dfm1).merge(dfm2)
	df['likes_per_msg'] = df['likes_received']/df['msg_cnt']
	return df

def chart_scatter_likes_by_day(df):
	"""todo: wip"""
	return 0
	# data = [go.Scatter(
          # x=days.day,
          # y=days[days['name']=='Ian Marshall']['msg_likes']
		  # ]
	
	# fig=go.Figure(data=data)
	# plt = py.plot(fig, filename='likes.html')
	
def chart_total_likes_by_username(df):
	data = [
		go.Bar(
			x=df['name'], # assign x as the dataframe column 'x'
			y=df['likes_per_msg'],
			name='Likes Per Message'
		),
	]

	layout = go.Layout(
		#barmode='group',
		title='Likes/Message'
	)

	fig = go.Figure(data=data, layout=layout)

	# IPython notebook
	# py.iplot(fig, filename='pandas-bar-chart-layout')

	plt = py.plot(fig)
	
def chart_likes_given_vs_received(df):
	data = [
		go.Bar(
			x=df['name'], # assign x as the dataframe column 'x'
			y=df['likes_given'],
			name='Likes Given'
		),
		go.Bar(
			x=df['name'],
			y=df['likes_received'],
			name = 'Likes Received'
		),

	]

	layout = go.Layout(
		barmode='group',
		title='Likes Given v.s. Likes Received'
	)

	fig = go.Figure(data=data, layout=layout)

	# IPython notebook
	# py.iplot(fig, filename='pandas-bar-chart-layout')

	plt = py.plot(fig)
	
if __name__ == '__main__':
	"""flags --stats, --charts, --all"""
	all = "--all" in sys.argv
	stats = "--stats" in sys.argv
	charts = "--charts" in sys.argv
	all = all or (not stats and not charts)

	
	cdata = get_convo_data('conversation.json')
	mdata = likes_by_id('message.json')

	# stat 1 - kinda lame
	# print("\nTotal messages per userid")
	# print(df_total_msg_by_user_id(cdata, mdata))

	df = df_like_ratios(cdata, mdata)
	if (all or stats):
		print("\nTotal likes per user")
		print(df_likes_per_username(cdata, mdata))

		print("\nLikes per message & given vs received likes")
		print(df)
	
	if (all or charts):
		chart_total_likes_by_username(df)
		chart_likes_given_vs_received(df)
