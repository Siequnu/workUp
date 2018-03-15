from app import workUpApp
from app import db

from app.models import Post, Download
import app.models

import string

def getAllUploadedPostsWithFilenameAndUsername ():
		return Post.getAllUploadedPostsWithFilenameAndUsername()
		
def getAllUploadedPostsCount():
		return Post.getAllUploadedPostsCount()
		
def getPostInfoFromUserId (userId):
	postInfo = Post.getPostInfoFromUserId (userId)
	cleanDict = {}
	for info in postInfo:
		# Get upload time
		datetime = info[1] #2018-02-25 21:50:13.750276
		splitDatetime = str.split(str(datetime)) #['2018-02-25', '21:50:13.750276']
		date = splitDatetime[0]
		timeSplit = str.split(splitDatetime[1], ':') #['21', '50', '13.750276']
		uploadTime = str(timeSplit[0]) + ':' + str(timeSplit[1])
		uploadDateAndtime = date + ' ' + uploadTime
		
		# Get completed comment count from file ID
		fileId = app.models.selectFromDb(['id'], 'post', [(str('filename="' + str(info[2]) + '"'))])
		conditions = []
		conditions.append(string.join(('fileid=', str(fileId[0][0])), ''))
		conditions.append('pending=0')
		peerReviewCount = app.models.selectFromDb(['id'], 'comment', conditions)
		
		# Add arrayed information to a new dictionary entry
		cleanDict[str(info[0])] = [uploadDateAndtime, str(len(peerReviewCount)), str(info[3])]
		
	return cleanDict