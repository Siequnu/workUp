from app import workUpApp
from app import db

from app.models import Post, Download

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
		# Get download count
		downloadCount = Download.getDownloadCountFromFilename(str(info[2]))
		
		# Add arrayed information to a new dictionary entry
		cleanDict[str(info[0])] = [uploadDateAndtime, str(downloadCount), str(info[3])]
		
	return cleanDict