# Jeff Stern, Analysis of Data

# Users Columns: Username,SharedProjects,FavoriteProjects,StudiosFollowing,StudiosCurate,Following,Followers,JoinDate,Location,Bio,Status
# Thrds Columns: ThreadURL,ThreadTitle,StartedUsername,Replies,Views,LastUpdated,LastRespondedUsername
postsColumns =   ["PostURL","PostID","Timestamp","Post","PostHTML","Username","PostNumber","Edited","EditDate","Signature","SignatureHTML"] 

import pandas as pd

users = pd.read_csv("users.csv")
posts = pd.read_csv("posts.csv", names=postsColumns)
threads = pd.read_csv("threads.csv")