from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics import accuracy_score


def main():
    root = Path(__file__).resolve().parents[1]
    dataset_path = root / 'dataset' / 'learner_history.csv'
    artifact_dir = root / 'ml' / 'artifacts'
    artifact_dir.mkdir(parents=True, exist_ok=True)

    if not dataset_path.exists():
        raise FileNotFoundError(f'Learner history dataset missing: {dataset_path}. Run generate_data.py first.')

    df = pd.read_csv(dataset_path)

    topic_encoder = LabelEncoder()
    skill_encoder = LabelEncoder()

    df['topic_encoded'] = topic_encoder.fit_transform(df['topic'])
    y = skill_encoder.fit_transform(df['skill_label'])

    feature_cols = ['avg_score', 'avg_time', 'consistency', 'overall_points', 'topic_encoded']
    X = df[feature_cols].values

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    X_scaled_full = scaler.transform(X)

    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    rf = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42)

    dt.fit(X_train_scaled, y_train)
    rf.fit(X_train_scaled, y_train)

    dt_acc = accuracy_score(y_test, dt.predict(X_test_scaled))
    rf_acc = accuracy_score(y_test, rf.predict(X_test_scaled))

    knn = NearestNeighbors(n_neighbors=5, metric='euclidean')
    knn.fit(X_scaled_full)

    joblib.dump(dt, artifact_dir / 'decision_tree.joblib')
    joblib.dump(rf, artifact_dir / 'random_forest.joblib')
    joblib.dump(knn, artifact_dir / 'knn.joblib')
    joblib.dump(scaler, artifact_dir / 'scaler.joblib')
    joblib.dump(topic_encoder, artifact_dir / 'topic_encoder.joblib')
    joblib.dump(skill_encoder, artifact_dir / 'skill_encoder.joblib')
    joblib.dump(df[['topic', 'skill_label']], artifact_dir / 'history_meta.joblib')

    print(f'DecisionTree accuracy: {dt_acc:.4f}')
    print(f'RandomForest accuracy: {rf_acc:.4f}')
    print(f'Artifacts saved to: {artifact_dir}')


if __name__ == '__main__':
    main()
