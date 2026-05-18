import argparse
import os
import random
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, wait
from pathlib import Path
from statistics import mean

from agent import (
    choose_action,
    choose_best_action,
    exploration_rate_for_generation,
    learn,
)
from dino_interface import get_state_bucket
from dino_interface import DinoRunnerInterface
from q_table_manager import load_q_table, q_table, save_q_table
from training_graph import TrainingGraph


DEFAULT_WORKERS = max(1, (os.cpu_count() or 2) - 2)
DEFAULT_EPISODES_PER_WORKER = 40
DEFAULT_EVALUATION_EPISODES = 10
DEFAULT_MAX_STEPS = 5000
BATCH_MERGE_RATE = 0.7
BEST_Q_TABLE_PATH = Path("best_q_table.json")


def copy_q_table(source):
    return {
        state_bucket: {action: value for action, value in q_values.items()}
        for state_bucket, q_values in source.items()
    }


def run_training_episode(exploration_rate, max_steps, visits):
    env = DinoRunnerInterface()
    state = env.reset()
    state_bucket = get_state_bucket(state)
    done = False
    score = 0

    while not done and score < max_steps:
        action = choose_action(state_bucket, exploration_rate=exploration_rate)
        next_state, reward, done, info = env.step(action)
        next_state_bucket = get_state_bucket(next_state)

        learn(state_bucket, action, reward, next_state_bucket, done)
        visits[(state_bucket, action)] += 1

        state_bucket = next_state_bucket
        score = info["score"]

    return score


def train_worker(worker_id, start_table, exploration_rate, episodes, max_steps, seed):
    random.seed(seed)
    q_table.clear()
    q_table.update(copy_q_table(start_table))

    visits = Counter()
    scores = []

    for _episode in range(episodes):
        scores.append(run_training_episode(exploration_rate, max_steps, visits))

    return {
        "worker_id": worker_id,
        "q_table": copy_q_table(q_table),
        "visits": visits,
        "episodes": episodes,
        "best_score": max(scores) if scores else 0,
        "average_score": mean(scores) if scores else 0,
    }


def merge_worker_results(results):
    weighted_values = {}
    weights = Counter()

    for result in results:
        worker_table = result["q_table"]
        visits = result["visits"]

        for key, count in visits.items():
            state_bucket, action = key
            value = worker_table[state_bucket][action]
            weighted_values[key] = weighted_values.get(key, 0.0) + value * count
            weights[key] += count

    for key, total_value in weighted_values.items():
        state_bucket, action = key
        batch_value = total_value / weights[key]

        if state_bucket not in q_table:
            q_table[state_bucket] = {0: 0.0, 1: 0.0}

        old_value = q_table[state_bucket][action]
        q_table[state_bucket][action] = old_value + BATCH_MERGE_RATE * (
            batch_value - old_value
        )


def evaluate_model(episodes, max_steps):
    scores = []

    for _episode in range(episodes):
        env = DinoRunnerInterface()
        state = env.reset()
        state_bucket = get_state_bucket(state)
        done = False
        score = 0

        while not done and score < max_steps:
            action = choose_best_action(state_bucket)
            next_state, _reward, done, info = env.step(action)
            state_bucket = get_state_bucket(next_state)
            score = info["score"]

        scores.append(score)

    return {
        "average_score": round(mean(scores)) if scores else 0,
        "best_score": max(scores) if scores else 0,
    }


def submit_batch(executor, args, generation, start_table):
    exploration_rate = exploration_rate_for_generation(generation)
    seed_base = time.time_ns()

    return [
        executor.submit(
            train_worker,
            worker_id,
            start_table,
            exploration_rate,
            args.episodes_per_worker,
            args.max_steps,
            seed_base + worker_id,
        )
        for worker_id in range(args.workers)
    ]


def collect_batch(futures, graph):
    pending = set(futures)
    results = []

    while pending:
        finished, pending = wait(pending, timeout=0.05)

        for future in finished:
            results.append(future.result())

        if graph is not None:
            graph.tick()

    return results


def train(args):
    load_q_table(args.q_table_path)

    graph = None if args.no_graph else TrainingGraph()
    best_model_score = 0
    start_time = time.perf_counter()

    print(
        f"training with {args.workers} workers, "
        f"{args.episodes_per_worker} episodes per worker"
    )

    try:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            generation = 1

            while args.batches is None or generation <= args.batches:
                exploration_rate = exploration_rate_for_generation(generation)
                start_table = copy_q_table(q_table)
                futures = submit_batch(executor, args, generation, start_table)
                results = collect_batch(futures, graph)

                merge_worker_results(results)
                evaluation = evaluate_model(args.evaluation_episodes, args.max_steps)
                population_score = max(result["best_score"] for result in results)
                episodes = sum(result["episodes"] for result in results)

                save_q_table(args.q_table_path)

                if evaluation["average_score"] > best_model_score:
                    best_model_score = evaluation["average_score"]
                    save_q_table(args.best_table_path)

                if graph is not None:
                    graph.record_generation(
                        generation=generation,
                        model_score=evaluation["average_score"],
                        population_score=population_score,
                        q_states=len(q_table),
                        exploration_rate=exploration_rate,
                    )

                elapsed = time.perf_counter() - start_time
                print(
                    f"batch {generation} | "
                    f"episodes {episodes} | "
                    f"explore {exploration_rate:.0%} | "
                    f"model avg {evaluation['average_score']} | "
                    f"model best {evaluation['best_score']} | "
                    f"population best {population_score} | "
                    f"q states {len(q_table)} | "
                    f"{elapsed:.1f}s"
                )

                generation += 1

    except KeyboardInterrupt:
        print("stopping after keyboard interrupt")
    finally:
        save_q_table(args.q_table_path)

        if graph is not None:
            graph.close()


def parse_args():
    parser = argparse.ArgumentParser(description="Fast headless Q-learning trainer.")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument(
        "--episodes-per-worker",
        type=int,
        default=DEFAULT_EPISODES_PER_WORKER,
    )
    parser.add_argument(
        "--evaluation-episodes",
        type=int,
        default=DEFAULT_EVALUATION_EPISODES,
    )
    parser.add_argument("--max-steps", type=int, default=DEFAULT_MAX_STEPS)
    parser.add_argument("--batches", type=int, default=None)
    parser.add_argument("--no-graph", action="store_true")
    parser.add_argument(
        "--q-table-path",
        type=Path,
        default=Path("q_table.json"),
    )
    parser.add_argument(
        "--best-table-path",
        type=Path,
        default=BEST_Q_TABLE_PATH,
    )
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
