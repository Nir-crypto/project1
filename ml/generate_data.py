import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def generate_rows(n_samples: int, seed: int):
    rng = np.random.default_rng(seed)
    topics = np.array(['Python', 'JavaScript', 'Data Science'])

    rows = []
    for _ in range(n_samples):
        topic = rng.choice(topics)
        base_skill = rng.choice(['Beginner', 'Intermediate', 'Advanced'], p=[0.4, 0.35, 0.25])

        if base_skill == 'Beginner':
            avg_score = rng.normal(45, 10)
            avg_time = rng.normal(28, 6)
            consistency = rng.normal(0.35, 0.15)
        elif base_skill == 'Intermediate':
            avg_score = rng.normal(68, 8)
            avg_time = rng.normal(20, 5)
            consistency = rng.normal(0.55, 0.12)
        else:
            avg_score = rng.normal(86, 7)
            avg_time = rng.normal(14, 4)
            consistency = rng.normal(0.75, 0.1)

        avg_score = float(np.clip(avg_score, 5, 100))
        avg_time = float(np.clip(avg_time, 5, 60))
        consistency = float(np.clip(consistency, 0, 1))

        time_factor = np.clip(1 - (avg_time / 20.0), 0, 1)
        overall_points = round(float(70 * (avg_score / 100.0) + 20 * time_factor + 10 * consistency), 2)

        if overall_points < 50:
            skill_label = 'Beginner'
        elif overall_points < 75:
            skill_label = 'Intermediate'
        else:
            skill_label = 'Advanced'

        rows.append(
            {
                'avg_score': round(avg_score, 2),
                'avg_time': round(avg_time, 2),
                'consistency': round(consistency, 4),
                'overall_points': overall_points,
                'topic': topic,
                'skill_label': skill_label,
            }
        )

    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic learner history data.')
    parser.add_argument('--samples', type=int, default=400, help='Number of synthetic rows to generate.')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility.')
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    dataset_dir = project_root / 'dataset'
    dataset_dir.mkdir(parents=True, exist_ok=True)

    output_file = dataset_dir / 'learner_history.csv'
    df = generate_rows(args.samples, args.seed)
    df.to_csv(output_file, index=False)
    print(f'Generated {len(df)} rows at {output_file}')


if __name__ == '__main__':
    main()
