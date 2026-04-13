import time


def main() -> None:
    print("worker download-service listo", flush=True)
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
