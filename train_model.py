import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle

# load dataset
data = pd.read_csv("dataset/transactions.csv")

X = data["Description"]
y = data["Category"]

# text vectorization
vectorizer = TfidfVectorizer()

X_vec = vectorizer.fit_transform(X)

# split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X_vec, y, test_size=0.2, random_state=42)

# model
model = LogisticRegression()

model.fit(X_train, y_train)

# save model
pickle.dump(model, open("model/model.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("Model trained and saved!")