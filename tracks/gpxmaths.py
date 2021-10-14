import json
from pymongo import MongoClient
import gpxpy
import pandas as pd
from matplotlib import pyplot

mongo_uri = "mongodb://localhost:27017"
mongo_db = "tracks"
mongo_collection = "trailwatch"

client = MongoClient(mongo_uri)
db = client[mongo_db]
collection = db[mongo_collection]

print(collection.count())

keys = collection.find_one().keys()
values = [track.values() for track in collection.find()]

df = pd.DataFrame(columns=keys, data=values).set_index("_id")
df.dropna()
df['ascent'] = df['ascent'].astype(float)
df['descent'] = df['descent'].astype(float)
df['downhill'] = df['downhill'].astype(float)
df['uphill'] = df['uphill'].astype(float)
df['highest_ele'] = df['highest_ele'].astype(float)
df['lowest_ele'] = df['lowest_ele'].astype(float)
df['length_2d'] = df['length_2d'].astype(float)
df['length_3d'] = df['length_3d'].astype(float)
df['max_speed'] = df['max_speed'].astype(float)
df['avg_speed'] = df['length_3d']/df['moving_time']

df = df[df['moving_time'] > 0]
df = df[df['length_2d'] > 2000]
df = df[df['length_2d'] < 7000]

df = df[df['avg_speed'] < 2]
df = df[df['avg_speed'] > 0.2]

print (df.describe())
print (df.corr())

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import Normalizer
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error

y = df.reset_index()['moving_time']
x = df.reset_index()[['downhill', 'uphill', 'length_3d', 'highest_ele']]

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20, random_state=42)

lr = LinearRegression()
lr.fit(x_train, y_train)

y_pred_lr = lr.predict(x_test)
r2 = r2_score(y_test, y_pred_lr)
mse = mean_squared_error(y_test, y_pred_lr)

print("r2:\t{}\nMSE: \t{}".format(r2, mse))

c = pd.DataFrame([y_pred_lr, y_test]).transpose()
c.columns = ['lr', 'test']
c['percentage'] = (c['test'] - c['lr']) / c['test']
print(c.describe())

coeff_df = pd.DataFrame(lr.coef_, x.columns, columns=['Coefficient'])
print(coeff_df)
print(lr.intercept_)