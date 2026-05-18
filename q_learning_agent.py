from dino_interface import DO_NOTHING, DinoRunnerInterface, get_state_bucket


def main():
    env = DinoRunnerInterface(seed=1)
    state = env.reset()

    for step in range(10):
        bucketed_state = get_state_bucket(state)
        print(f"step={step} raw={state} bucket={bucketed_state}")
        state, _reward, done, _info = env.step(DO_NOTHING)

        if done:
            break


if __name__ == "__main__":
    main()
