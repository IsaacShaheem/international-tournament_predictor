import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

df = pd.read_csv("data/results.csv")

print(df.head())

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

df["result"] = "Draw"

df.loc[df["home_score"] > df["away_score"], "result"] = "Home Win"
df.loc[df["away_score"] > df["home_score"], "result"] = "Away Win"

print("\nMatch Results")
print(df["result"].value_counts())

print("\nPercentages:")
print(df["result"].value_counts(normalize=True) * 100)

print("\nNeutral Site Matches:")
print(df["neutral"].value_counts())

print("\nResults in neutral matches:")
print(df[df["neutral"] == True] ["result"].value_counts(normalize=True) * 100)

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date")
print(df["date"].head())

df["neutral_flag"] = df["neutral"].astype(int)
print(df[["neutral","neutral_flag"]].head())

df["home_win"] = (df["home_score"] > df["away_score"]).astype(int)
print(df["home_win"].value_counts())

X = df[["neutral_flag"]]
y = df["home_win"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = LogisticRegression(solver="liblinear")

model.fit(X_train, y_train)

predictions = model.predict(X_test)

print("\nModel Accuracy:")
print(accuracy_score(y_test, predictions))

print("\nMost frequent home teams:")
print(df["home_team"].value_counts().head(10))